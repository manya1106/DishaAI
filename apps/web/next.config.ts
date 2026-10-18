import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // cacheComponents (+ partialPrefetching, which depends on it) kept
  // previously-visited client pages' React state alive across soft
  // navigations — e.g. /new-analysis re-showing a finished "running
  // the swarm" screen instead of a fresh step-1 form. Disabled: nothing
  // in this app needs that caching, and it broke the wizard's basic
  // "clicking New Analysis always starts fresh" expectation.
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
