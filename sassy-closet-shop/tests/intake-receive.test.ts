import assert from "node:assert/strict";
import { describe, test } from "node:test";
import {
  applyStageResult,
  emptyStagedDocument,
  parseIntakeReceivePayload,
  parseStagedDocument,
  stageIntakeSubmission,
  type CatalogMaIndex,
  type IntakeReceivePayload,
  type StagedIntakeRecord,
} from "../lib/intake-receive";

const NOW = "2026-09-25T08:00:00.000Z";
const EMPTY_CATALOG: CatalogMaIndex = { mas: new Set(), links: new Map() };

function payload(overrides: Partial<IntakeReceivePayload> = {}): IntakeReceivePayload {
  return {
    event: "create",
    ma: "A17",
    timestamp: "2026-09-25T07:00:00.000Z",
    source: "intake",
    ...overrides,
  };
}

function stagedRecord(overrides: Partial<StagedIntakeRecord> = {}): StagedIntakeRecord {
  return {
    ma: "A17",
    sourceLink: "https://item.taobao.com/item.htm?id=123",
    stage: "needs_research",
    priceUsd: null,
    proposedSell: null,
    proposedCost: null,
    proposedSizes: [],
    proposedColors: [],
    kind: null,
    photoCount: 0,
    firstStagedAt: NOW,
    lastSubmissionAt: "2026-09-25T07:00:00.000Z",
    submissionCount: 1,
    updatedAt: NOW,
    ...overrides,
  };
}

describe("parseIntakeReceivePayload", () => {
  test("accepts a valid create payload", () => {
    const result = parseIntakeReceivePayload(payload());
    assert.equal(result.ok, true);
    if (result.ok) {
      assert.equal(result.payload.ma, "A17");
      assert.equal(result.payload.event, "create");
    }
  });

  test("normalizes lowercase mã", () => {
    const result = parseIntakeReceivePayload(payload({ ma: "a17" }));
    assert.equal(result.ok, true);
    if (result.ok) assert.equal(result.payload.ma, "A17");
  });

  test("rejects an invalid mã", () => {
    const result = parseIntakeReceivePayload(payload({ ma: "ZZZ" }));
    assert.equal(result.ok, false);
  });

  test("rejects a bad event", () => {
    const result = parseIntakeReceivePayload({ ...payload(), event: "delete" });
    assert.equal(result.ok, false);
  });

  test("rejects a non-ISO timestamp", () => {
    const result = parseIntakeReceivePayload(payload({ timestamp: "yesterday" }));
    assert.equal(result.ok, false);
  });

  test("rejects a non-object body", () => {
    assert.equal(parseIntakeReceivePayload(null).ok, false);
    assert.equal(parseIntakeReceivePayload("nope").ok, false);
  });
});

describe("stageIntakeSubmission", () => {
  test("new mã stages at needs_research with Inbox giá (priceUsd null)", () => {
    const result = stageIntakeSubmission([], payload(), EMPTY_CATALOG, NOW);
    assert.equal(result.ok, true);
    if (result.ok) {
      assert.equal(result.status, "staged");
      assert.equal(result.record.ma, "A17");
      assert.equal(result.record.stage, "needs_research");
      assert.equal(result.record.priceUsd, null);
      assert.equal(result.record.submissionCount, 1);
    }
  });

  test("proposed sell/sizes/colors are recorded but never go public", () => {
    const result = stageIntakeSubmission(
      [],
      payload({ sell: "28", sizes: ["S", "M"], colors: ["Pink"] }),
      EMPTY_CATALOG,
      NOW,
    );
    assert.equal(result.ok, true);
    if (result.ok) {
      assert.equal(result.record.priceUsd, null);
      assert.equal(result.record.proposedSell, "28");
      assert.deepEqual(result.record.proposedSizes, ["S", "M"]);
      assert.deepEqual(result.record.proposedColors, ["Pink"]);
    }
  });

  test("same mã + same timestamp is a duplicate", () => {
    const existing = [stagedRecord()];
    const result = stageIntakeSubmission([], payload(), EMPTY_CATALOG, NOW);
    assert.equal(result.ok, true);
    const dup = stageIntakeSubmission(existing, payload(), EMPTY_CATALOG, NOW);
    assert.equal(dup.ok, true);
    if (dup.ok) assert.equal(dup.status, "duplicate");
    if (result.ok) assert.equal(result.status, "staged");
  });

  test("same mã + new timestamp updates without touching mã/link", () => {
    const existing = [stagedRecord()];
    const result = stageIntakeSubmission(
      existing,
      payload({ event: "update", timestamp: "2026-09-25T07:30:00.000Z", sell: "29" }),
      EMPTY_CATALOG,
      NOW,
    );
    assert.equal(result.ok, true);
    if (result.ok) {
      assert.equal(result.status, "updated");
      assert.equal(result.record.ma, "A17");
      assert.equal(result.record.sourceLink, "https://item.taobao.com/item.htm?id=123");
      assert.equal(result.record.proposedSell, "29");
      assert.equal(result.record.priceUsd, null);
      assert.equal(result.record.submissionCount, 2);
    }
  });

  test("conflicting source link for a known mã is rejected (never remint)", () => {
    const existing = [stagedRecord()];
    const result = stageIntakeSubmission(
      existing,
      payload({
        timestamp: "2026-09-25T07:30:00.000Z",
        source_link: "https://item.taobao.com/item.htm?id=999",
      }),
      EMPTY_CATALOG,
      NOW,
    );
    assert.equal(result.ok, false);
  });

  test("conflicting link against the live catalog is rejected", () => {
    const catalog: CatalogMaIndex = {
      mas: new Set(["A17"]),
      links: new Map([["A17", "https://item.taobao.com/item.htm?id=123"]]),
    };
    const result = stageIntakeSubmission(
      [],
      payload({ source_link: "https://item.taobao.com/item.htm?id=999" }),
      catalog,
      NOW,
    );
    assert.equal(result.ok, false);
  });

  test("matching link against the live catalog is accepted", () => {
    const catalog: CatalogMaIndex = {
      mas: new Set(["A17"]),
      links: new Map([["A17", "https://item.taobao.com/item.htm?id=123"]]),
    };
    const result = stageIntakeSubmission(
      [],
      payload({ source_link: "https://item.taobao.com/item.htm?id=123" }),
      catalog,
      NOW,
    );
    assert.equal(result.ok, true);
  });
});

describe("applyStageResult + parseStagedDocument", () => {
  test("staged result appends; duplicate leaves the document alone", () => {
    const doc = emptyStagedDocument(NOW);
    const staged = stageIntakeSubmission([], payload(), EMPTY_CATALOG, NOW);
    assert.equal(staged.ok, true);
    if (!staged.ok) return;
    const next = applyStageResult(doc, staged, NOW);
    assert.equal(next.records.length, 1);

    const dup = stageIntakeSubmission(next.records, payload(), EMPTY_CATALOG, NOW);
    assert.equal(dup.ok, true);
    if (!dup.ok) return;
    assert.equal(dup.status, "duplicate");
    const same = applyStageResult(next, dup, NOW);
    assert.equal(same.records.length, 1);
  });

  test("parseStagedDocument drops invalid records and bad schemas", () => {
    const good = parseStagedDocument(
      { schema: "intake-staged.v1", records: [stagedRecord()] },
      NOW,
    );
    assert.equal(good.records.length, 1);
    const bad = parseStagedDocument({ schema: "nope", records: [] }, NOW);
    assert.equal(bad.records.length, 0);
    const mixed = parseStagedDocument(
      {
        schema: "intake-staged.v1",
        records: [stagedRecord(), { ma: "ZZZ", stage: "needs_research" }],
      },
      NOW,
    );
    assert.equal(mixed.records.length, 1);
  });
});
