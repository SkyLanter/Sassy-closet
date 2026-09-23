import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { get, put } from "@vercel/blob";
import { createClient } from "@vercel/kv";
import { getCatalogStorageInfo } from "@/lib/catalog-store";
import { emptyPipelineDocument, parsePipelineDocument, type PipelineDocument } from "@/lib/pipeline";
import { siteId } from "@/lib/site-runtime";

/**
 * Pipeline tracker persistence. Uses the SAME catalog storage backends
 * (Blob → KV → local file), never a new backend. The tracker lives in its own
 * object (pipeline.v1.json) so the catalog contract, save receipts, and
 * round-trip verification stay untouched.
 */

export function pipelineBlobPath(id = siteId()): string {
  return `${id}/pipeline.v1.json`;
}

export function pipelineKvKey(id = siteId()): string {
  return `${id}:pipeline.v1`;
}

const LOCAL_PIPELINE_REL = path.join("data", "live-pipeline.json");

function kvClient() {
  const url = process.env.KV_REST_API_URL?.trim();
  const token = process.env.KV_REST_API_TOKEN?.trim();
  if (!url || !token) {
    return null;
  }
  return createClient({ url, token });
}

function localPipelinePath(): string {
  return path.join(process.cwd(), LOCAL_PIPELINE_REL);
}

function localPersistAllowed(): boolean {
  return process.env.VERCEL !== "1";
}

function serialize(document: PipelineDocument): string {
  return `${JSON.stringify(parsePipelineDocument(document, document.siteId || siteId()), null, 2)}\n`;
}

export async function readPipelineRecord(): Promise<PipelineDocument | null> {
  const info = getCatalogStorageInfo();
  const id = siteId();
  try {
    if (info.backend === "blob") {
      const result = await get(pipelineBlobPath(id), { access: "public", useCache: false });
      if (!result || result.statusCode !== 200 || !result.stream) {
        return null;
      }
      const text = await new Response(result.stream).text();
      return parsePipelineDocument(JSON.parse(text) as unknown, id);
    }
    if (info.backend === "kv") {
      const client = kvClient();
      if (!client) {
        return null;
      }
      const raw = await client.get<unknown>(pipelineKvKey(id));
      if (raw === null || raw === undefined) {
        return null;
      }
      return parsePipelineDocument(raw, id);
    }
    if (info.backend === "local" && localPersistAllowed()) {
      try {
        const text = await readFile(localPipelinePath(), "utf8");
        return parsePipelineDocument(JSON.parse(text) as unknown, id);
      } catch (error) {
        if (error && typeof error === "object" && "code" in error && (error as { code?: string }).code === "ENOENT") {
          return null;
        }
        throw error;
      }
    }
  } catch (error) {
    console.error("Pipeline tracker read failed.", error);
    return null;
  }
  return null;
}

export async function writePipelineRecord(document: PipelineDocument): Promise<PipelineDocument> {
  const info = getCatalogStorageInfo();
  if (!info.canWrite) {
    throw new Error(
      "Pipeline tracker has no store. Set BLOB_READ_WRITE_TOKEN (or KV) on Vercel; locally it writes data/live-pipeline.json.",
    );
  }
  const id = siteId();
  const clean = parsePipelineDocument(document, id);
  const stamped: PipelineDocument = { ...clean, updatedAt: new Date().toISOString() };
  const json = serialize(stamped);

  if (info.backend === "blob") {
    await put(pipelineBlobPath(id), json, {
      access: "public",
      addRandomSuffix: false,
      allowOverwrite: true,
      contentType: "application/json",
      cacheControlMaxAge: 0,
    });
    return stamped;
  }
  if (info.backend === "kv") {
    const client = kvClient();
    if (!client) {
      throw new Error("KV is not configured.");
    }
    await client.set(pipelineKvKey(id), stamped);
    return stamped;
  }
  const file = localPipelinePath();
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, json, "utf8");
  return stamped;
}

/** Read for admin pages — empty document when no store is attached. */
export async function readPipelineForAdmin(): Promise<PipelineDocument> {
  return (await readPipelineRecord()) ?? emptyPipelineDocument(siteId());
}
