export default function IntakeLoading() {
  return (
    <main className="mx-auto w-full max-w-md px-4 py-6 md:max-w-2xl" aria-busy="true" aria-live="polite">
      <div className="h-4 w-28 rounded-full bg-[#f3e6e2]" />
      <div className="mt-3 h-10 w-48 rounded-2xl bg-[#f3e6e2]" />
      <div className="mt-3 h-4 w-64 rounded-full bg-[#f3e6e2]" />
      <div className="mt-5 h-12 rounded-full bg-[#f3e6e2]" />
      <div className="mt-4 space-y-3 rounded-3xl bg-[#fffaf8] p-4 ring-1 ring-[#eadfdc]">
        <div className="h-11 rounded-xl bg-[#fbf6f4]" />
        <div className="h-24 rounded-2xl bg-[#fbf6f4]" />
        <div className="grid grid-cols-2 gap-2">
          <div className="h-11 rounded-xl bg-[#fbf6f4]" />
          <div className="h-11 rounded-xl bg-[#fbf6f4]" />
        </div>
      </div>
    </main>
  );
}
