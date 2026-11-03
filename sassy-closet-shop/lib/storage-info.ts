export type CatalogBackend = "blob" | "kv" | "local" | "seed";

export type CatalogStorageInfo = {
  backend: CatalogBackend;
  canWrite: boolean;
  canUpload: boolean;
  /** Where the last catalog read actually came from (must match backend after Save). */
  reading?: CatalogBackend;
};
