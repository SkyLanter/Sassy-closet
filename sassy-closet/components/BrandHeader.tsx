export function BrandHeader() {
  return (
    <header
      data-testid="brand-mark"
      className="relative mx-auto mb-5 w-full max-w-xl bg-transparent px-2 pb-1 pt-6 text-center lg:mb-8"
    >
      <h1
        data-testid="site-title"
        className="font-script relative mx-auto inline-block px-8 text-[2.7rem] font-normal leading-[1.28] text-[#D82B60] sm:px-10 sm:text-[3.15rem] lg:text-[3.35rem]"
      >
        Sassy Closet
      </h1>
      <p
        data-testid="intake-kicker"
        className="mt-0.5 text-[0.68rem] font-semibold uppercase tracking-[0.38em] text-[#D82B60] sm:text-[0.74rem] sm:tracking-[0.46em]"
      >
        INTAKE • NHẬN ĐỒ
      </p>
    </header>
  );
}
