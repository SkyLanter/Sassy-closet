import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { createClient } from "@vercel/kv";
import { getCatalogStorageInfo } from "@/lib/catalog-store";
import {
  emptyStagedDocument,
  parseStagedDocument,
  type IntakeStagedDocument,
} from "@/lib/intake-receive";
import { siteId } from "@/lib/site-runtime";

/**
 * Intake staging persistence. Uses the SAME catalog storage backends
 * (Blob → KV → local file), never a new backend. Staged intake records live
 * in their own object (intake-staged.v1.json) so the catalog contract, save
 * receipts, and round-trip verification stay untouched.
 *
 * Staged records are NOT the live catalog. Nothing here publishes, merges,
 * or marks Square stock — promotion to a sell tab is a separate, human-
 * approved step.
 *
 * Security: intake staging never touches public Blob. When the catalog
 * backend resolves to "blob", staging reads and writes via KV instead, and
 * writes fail closed if KV is not configured.
 */

export function intakeStagedBlobPath(id = siteId()): string {
  return `${id}/intake-staged.v1.json`;
}

export function intakeStagedKvKey(id = siteId()): string {
  return `${id}:intake-staged.v1`;
}

const LOCAL_STAGED_REL = path.join("data", "intake-staged.json");

function kvClient() {
  const url = process.env.KV_REST_API_URL?.trim();
  const token = process.env.KV_REST_API_TOKEN?.trim();
  if (!url || !token) {
    return null;
  }
  return createClient({ url, token });
}

function localStagedPath(): string {
  return path.join(process.cwd(), LOCAL_STAGED_REL);
}

function localPersistAllowed(): boolean {
  return process.env.VERCEL !== "1";
}

function serialize(document: IntakeStagedDocument): string {
  const now = new Date().toISOString();
  return `${JSON.stringify(parseStagedDocument(document, now), null, 2)}\n`;
}

export async function readStagedRecord(): Promise<IntakeStagedDocument | null> {
  const info = getCatalogStorageInfo();
  const id = siteId();
  const now = new Date().toISOString();
  try {
    if (info.backend === "blob") {
      // Public Blob is never read for intake staging; read via KV instead.
      const client = kvClient();
      if (!client) {
        return null;
      }
      const raw = await client.get<unknown>(intakeStagedKvKey(id));
      if (raw === null || raw === undefined) {
        return null;
      }
      return parseStagedDocument(raw, now);
    }
    if (info.backend === "kv") {
      const client = kvClient();
      if (!client) {
        return null;
      }
      const raw = await client.get<unknown>(intakeStagedKvKey(id));
      if (raw === null || raw === undefined) {
        return null;
      }
      return parseStagedDocument(raw, now);
    }
    if (info.backend === "local" && localPersistAllowed()) {
      try {
        const text = await readFile(localStagedPath(), "utf8");
        return parseStagedDocument(JSON.parse(text) as unknown, now);
      } catch (error) {
        if (error && typeof error === "object" && "code" in error && (error as { code?: string }).code === "ENOENT") {
          return null;
        }
        throw error;
      }
    }
  } catch (error) {
    console.error("Intake staged read failed.", error);
    return null;
  }
  return null;
}

export async function writeStagedRecord(
  document: IntakeStagedDocument,
): Promise<IntakeStagedDocument> {
  const info = getCatalogStorageInfo();
  if (!info.canWrite) {
    throw new Error(
      "Intake staging has no store. Set BLOB_READ_WRITE_TOKEN (or KV) on Vercel; locally it writes data/intake-staged.json.",
    );
  }
  const id = siteId();
  const now = new Date().toISOString();
  const clean = parseStagedDocument(document, now);
  const stamped: IntakeStagedDocument = { ...clean, updatedAt: now };
  const json = serialize(stamped);

  if (info.backend === "blob") {
    // Refuse public Blob for intake staging; write via KV, or fail closed.
    const client = kvClient();
    if (!client) {
      throw new Error("Intake staging refuses public Blob. Configure KV for intake staging.");
    }
    await client.set(intakeStagedKvKey(id), stamped);
    return stamped;
  }
  if (info.backend === "kv") {
    const client = kvClient();
    if (!client) {
      throw new Error("KV is not configured.");
    }
    await client.set(intakeStagedKvKey(id), stamped);
    return stamped;
  }
  const file = localStagedPath();
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, json, "utf8");
  return stamped;
}

/** Read for the receive endpoint — empty document when nothing is staged yet. */
export async function readStagedForReceive(): Promise<IntakeStagedDocument> {
  return (await readStagedRecord()) ?? emptyStagedDocument(new Date().toISOString());
}
