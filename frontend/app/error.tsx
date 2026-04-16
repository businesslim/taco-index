"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("App error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 p-6 text-center">
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <pre className="text-xs text-left bg-gray-900 text-red-400 p-4 rounded-lg max-w-full overflow-auto whitespace-pre-wrap break-all">
        {error.message}
        {"\n\n"}
        {error.stack}
      </pre>
      <button
        onClick={reset}
        className="px-4 py-2 bg-gray-700 rounded-lg text-sm"
      >
        Try again
      </button>
    </div>
  );
}
