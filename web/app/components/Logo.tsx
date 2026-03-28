/** Shared logo icon + wordmark for GoldLine branding. */

/** Gold pen-nib icon in a rounded-square container. */
export function LogoIcon({ size = "md" }: { size?: "sm" | "md" | "lg" | "xl" }) {
  const dims = { sm: "h-8 w-8", md: "h-9 w-9", lg: "h-10 w-10", xl: "h-16 w-16" };
  const iconDims = { sm: 16, md: 18, lg: 20, xl: 32 };
  const px = iconDims[size];

  return (
    <div
      className={`${dims[size]} flex shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 shadow-lg shadow-amber-500/25`}
    >
      <svg width={px} height={px} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Pen / quill icon — evokes office supplies */}
        <path
          d="M3 21l3.25-1.25a2 2 0 0 0 .9-.7L18.3 4.8a1.5 1.5 0 0 0-.05-2.05l-.95-.95a1.5 1.5 0 0 0-2.05-.05L4.95 12.85a2 2 0 0 0-.7.9L3 17v4z"
          fill="#18181b"
          fillOpacity="0.85"
        />
        <path
          d="M14.5 4.5l5 5"
          stroke="#18181b"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <path
          d="M3 21l2-6"
          stroke="#18181b"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

/** Ghost variant for chat panel / welcome screen — translucent bg with amber icon. */
export function LogoIconGhost({ size = "md" }: { size?: "md" | "lg" | "xl" }) {
  const dims = { md: "h-9 w-9", lg: "h-14 w-14", xl: "h-18 w-18" };
  const iconDims = { md: 18, lg: 26, xl: 34 };
  const px = iconDims[size];

  return (
    <div
      className={`${dims[size]} flex shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400/15 to-amber-600/15 ring-1 ring-amber-500/20`}
    >
      <svg width={px} height={px} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M3 21l3.25-1.25a2 2 0 0 0 .9-.7L18.3 4.8a1.5 1.5 0 0 0-.05-2.05l-.95-.95a1.5 1.5 0 0 0-2.05-.05L4.95 12.85a2 2 0 0 0-.7.9L3 17v4z"
          fill="currentColor"
          fillOpacity="0.85"
          className="text-amber-400"
        />
        <path d="M14.5 4.5l5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="text-amber-400" />
        <path d="M3 21l2-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="text-amber-400" />
      </svg>
    </div>
  );
}

/** Full wordmark: "Gold" (gradient) + "Line" (white). */
export function Wordmark({ className = "text-sm" }: { className?: string }) {
  return (
    <span className={`font-semibold tracking-tight ${className}`}>
      <span className="bg-gradient-to-r from-amber-400 to-amber-500 bg-clip-text text-transparent">Gold</span>
      <span className="text-zinc-100">Line</span>
      <span className="ml-1.5 font-normal text-zinc-500">Office Supplies</span>
    </span>
  );
}
