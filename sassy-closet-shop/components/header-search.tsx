"use client";

import {
  createContext,
  Suspense,
  useCallback,
  useContext,
  useEffect,
  useId,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
  type RefObject,
} from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { MaMark } from "@/components/ma-mark";
import { useShopSearch } from "@/components/shop-search";
import { displayName } from "@/lib/copy";
import {
  LOOK_SEARCH_ARIA,
  LOOK_SEARCH_CLOSE,
  LOOK_SEARCH_EMPTY,
  LOOK_SEARCH_PLACEHOLDER,
  LOOK_SEARCH_TOGGLE,
  lookSearchHref,
  resolveLookSearch,
  suggestLooks,
  type LookSearchItem,
} from "@/lib/look-search";

type HeaderSearchApi = {
  listId: string;
  fieldRef: RefObject<HTMLDivElement | null>;
  sheetRef: RefObject<HTMLDivElement | null>;
  inputRef: RefObject<HTMLInputElement | null>;
  expanded: boolean;
  value: string;
  suggestions: LookSearchItem[];
  showPanel: boolean;
  active: number | null;
  setOpen: (next: boolean) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void;
  onInputChange: (next: string) => void;
  onFocus: () => void;
  pickLook: (look: LookSearchItem) => void;
  closePanel: () => void;
};

const HeaderSearchContext = createContext<HeaderSearchApi | null>(null);

function SearchGlyph() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" aria-hidden>
      <path
        fill="currentColor"
        d="M10.5 3.8a6.7 6.7 0 0 1 5.2 10.9l4 4a.9.9 0 0 1-1.3 1.3l-4-4A6.7 6.7 0 1 1 10.5 3.8Zm0 1.7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z"
      />
    </svg>
  );
}

function UrlQueryReader({ onHomeQuery }: { onHomeQuery: (query: string) => void }) {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const homeQuery = pathname === "/" ? (searchParams.get("q") ?? "") : null;
  const previousHome = useRef<string | null>(null);

  useEffect(() => {
    if (homeQuery === null) {
      previousHome.current = null;
      return;
    }
    const prior = previousHome.current;
    previousHome.current = homeQuery;
    const trimmed = homeQuery.trim();
    if (trimmed) {
      onHomeQuery(trimmed);
      return;
    }
    if (prior !== null && prior.trim()) {
      onHomeQuery("");
    }
  }, [homeQuery, onHomeQuery]);

  return null;
}

function HeaderSearchState({
  urlQuery,
  onExpandedChange,
  children,
}: {
  urlQuery: string;
  onExpandedChange?: (expanded: boolean) => void;
  children: ReactNode;
}) {
  const router = useRouter();
  const listId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const fieldRef = useRef<HTMLDivElement>(null);
  const sheetRef = useRef<HTMLDivElement>(null);
  const { looks, draft, setDraft } = useShopSearch();
  const [expanded, setExpanded] = useState(false);
  const [suggestOpen, setSuggestOpen] = useState(false);
  const [active, setActive] = useState<number | null>(null);
  const value = draft ?? urlQuery;
  const suggestions = suggestLooks(looks, value);
  const showPanel = suggestOpen && value.trim().length > 0;

  const setOpen = useCallback(
    (next: boolean) => {
      setExpanded(next);
      onExpandedChange?.(next);
      if (!next) {
        setSuggestOpen(false);
        setActive(null);
      }
    },
    [onExpandedChange],
  );

  useEffect(() => {
    if (!expanded) {
      return;
    }
    inputRef.current?.focus();
  }, [expanded]);

  useEffect(() => {
    function onPointerDown(event: PointerEvent) {
      const target = event.target as Node;
      if (fieldRef.current?.contains(target) || sheetRef.current?.contains(target)) {
        return;
      }
      setSuggestOpen(false);
      setExpanded(false);
      onExpandedChange?.(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [onExpandedChange]);

  function closePanel() {
    setDraft(value.trim());
    setSuggestOpen(false);
    setActive(null);
    setOpen(false);
  }

  function pickLook(look: LookSearchItem) {
    closePanel();
    router.push(`/m/${look.ma}`);
  }

  function commit(raw: string) {
    const resolution = resolveLookSearch(looks, raw);
    setDraft(raw.trim());
    setSuggestOpen(false);
    setActive(null);
    setOpen(false);
    router.push(lookSearchHref(resolution));
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const picked = active !== null ? suggestions[active] : undefined;
    if (picked) {
      pickLook(picked);
      return;
    }
    commit(value);
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    switch (event.key) {
      case "ArrowDown":
        if (!suggestions.length) {
          return;
        }
        event.preventDefault();
        setSuggestOpen(true);
        setActive((current) => {
          if (current === null) {
            return 0;
          }
          return (current + 1) % suggestions.length;
        });
        break;
      case "ArrowUp":
        if (!suggestions.length) {
          return;
        }
        event.preventDefault();
        setSuggestOpen(true);
        setActive((current) => {
          if (current === null) {
            return suggestions.length - 1;
          }
          return (current - 1 + suggestions.length) % suggestions.length;
        });
        break;
      case "Escape":
        event.preventDefault();
        if (suggestOpen) {
          setSuggestOpen(false);
          setActive(null);
          return;
        }
        setOpen(false);
        inputRef.current?.blur();
        break;
      default:
        return;
    }
  }

  const api: HeaderSearchApi = {
    listId,
    fieldRef,
    sheetRef,
    inputRef,
    expanded,
    value,
    suggestions,
    showPanel,
    active,
    setOpen,
    onSubmit,
    onKeyDown,
    onInputChange: (next: string) => {
      setDraft(next);
      setActive(null);
      setSuggestOpen(true);
    },
    onFocus: () => {
      setSuggestOpen(value.trim().length > 0);
    },
    pickLook,
    closePanel,
  };

  return <HeaderSearchContext.Provider value={api}>{children}</HeaderSearchContext.Provider>;
}

function useHeaderSearch(): HeaderSearchApi {
  const api = useContext(HeaderSearchContext);
  if (!api) {
    throw new Error("Header search controls must sit under HeaderSearchProvider");
  }
  return api;
}

export function HeaderSearchProvider({
  children,
  onExpandedChange,
}: {
  children: ReactNode;
  onExpandedChange?: (expanded: boolean) => void;
}) {
  const { setDraft } = useShopSearch();
  const [urlQuery, setUrlQuery] = useState("");
  const onHomeQuery = useCallback(
    (query: string) => {
      const trimmed = query.trim();
      setUrlQuery(trimmed);
      setDraft(trimmed ? trimmed : null);
    },
    [setDraft],
  );

  return (
    <HeaderSearchState urlQuery={urlQuery} onExpandedChange={onExpandedChange}>
      <Suspense fallback={null}>
        <UrlQueryReader onHomeQuery={onHomeQuery} />
      </Suspense>
      {children}
    </HeaderSearchState>
  );
}

export function HeaderSearch() {
  const search = useHeaderSearch();

  return (
    <div
      ref={search.fieldRef}
      className={`relative min-w-0 ${search.expanded ? "flex-1" : ""} sm:w-[12.5rem] lg:w-[14.5rem]`}
    >
      <div className="flex min-w-0 items-center justify-end gap-1">
        <button
          type="button"
          data-testid="shop-header-search-toggle"
          aria-expanded={search.expanded}
          aria-label={search.expanded ? LOOK_SEARCH_CLOSE : LOOK_SEARCH_TOGGLE}
          translate="no"
          onClick={() => {
            const next = !search.expanded;
            search.setOpen(next);
            if (next && search.value.trim().length > 0) {
              search.onFocus();
            }
          }}
          className="inline-flex min-h-11 min-w-11 shrink-0 touch-manipulation select-none items-center justify-center text-ink hover-hover:hover:text-gold-deep sm:hidden"
        >
          {search.expanded ? (
            <span className="text-lg leading-none" aria-hidden>
              ×
            </span>
          ) : (
            <SearchGlyph />
          )}
        </button>
        <form
          role="search"
          onSubmit={search.onSubmit}
          data-testid="shop-header-search"
          className={`${search.expanded ? "flex flex-1" : "hidden"} min-w-0 sm:flex`}
        >
          <label className="sr-only" htmlFor="shop-header-search-input">
            {LOOK_SEARCH_ARIA}
          </label>
          <input
            ref={search.inputRef}
            id="shop-header-search-input"
            type="search"
            role="combobox"
            name="q"
            value={search.value}
            autoComplete="off"
            autoCorrect="off"
            spellCheck={false}
            enterKeyHint="search"
            placeholder={LOOK_SEARCH_PLACEHOLDER}
            aria-label={LOOK_SEARCH_ARIA}
            aria-autocomplete="list"
            aria-controls={search.showPanel ? search.listId : undefined}
            aria-expanded={search.showPanel}
            aria-activedescendant={
              search.showPanel && search.active !== null && search.suggestions[search.active]
                ? `${search.listId}-${search.suggestions[search.active].ma}`
                : undefined
            }
            translate="no"
            onChange={(event) => search.onInputChange(event.target.value)}
            onFocus={search.onFocus}
            onKeyDown={search.onKeyDown}
            className="min-h-11 w-full min-w-0 rounded-full border border-gold/35 bg-transparent px-3 text-[13px] text-ink placeholder:text-muted focus:border-gold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
          />
        </form>
      </div>
    </div>
  );
}

export function HeaderSearchSheet() {
  const search = useHeaderSearch();
  if (!search.showPanel) {
    return null;
  }

  return (
    <div
      ref={search.sheetRef}
      id="shop-search-suggest"
      data-testid="shop-search-sheet"
      className="shop-search-sheet absolute inset-x-0 top-full z-[70] max-h-[min(70dvh,24rem)] overflow-y-auto border-t border-gold/35"
    >
      <ul
        id={search.listId}
        role="listbox"
        aria-label={LOOK_SEARCH_ARIA}
        data-testid="shop-header-search-hits"
        className="py-1"
      >
        {search.suggestions.length === 0 ? (
          <li
            className="px-[max(1.25rem,env(safe-area-inset-left,0px))] py-4 pr-[max(1.25rem,env(safe-area-inset-right,0px))] text-left text-[15px] leading-[1.5] text-ink sm:px-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]"
            role="option"
            aria-selected={false}
            translate="no"
          >
            {LOOK_SEARCH_EMPTY}
          </li>
        ) : (
          search.suggestions.map((look, index) => (
            <li key={look.ma} role="presentation">
              <Link
                id={`${search.listId}-${look.ma}`}
                href={`/m/${look.ma}`}
                role="option"
                aria-selected={index === search.active}
                data-testid="shop-header-search-hit"
                data-ma={look.ma}
                translate="no"
                onClick={search.closePanel}
                className={`flex min-h-11 touch-manipulation select-none items-center gap-2 px-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] text-left text-[13px] sm:px-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))] ${
                  index === search.active ? "bg-blush text-ink" : "text-ink hover-hover:hover:bg-blush"
                }`}
              >
                <MaMark ma={look.ma} className="text-[11px] tracking-[0.14em] text-gold-deep" />
                <span className="min-w-0 truncate">{displayName(look)}</span>
              </Link>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
