export function AdminSignOut() {
  return (
    <form
      method="post"
      action="/api/admin/logout"
      className="mx-auto flex w-full max-w-6xl justify-end px-4 pt-4 sm:px-6"
    >
      <button
        type="submit"
        className="inline-flex min-h-11 touch-manipulation items-center text-sm text-muted hover-hover:hover:text-ink"
      >
        Sign out
      </button>
    </form>
  );
}
