import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { App } from "./App";

describe("App", () => {
  test("renders the Uzbek landing page with primary sections", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /^Aviora Dialogue$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^Kirish$/i })).toHaveAttribute("href", "/signin");
    expect(screen.getByText(/Aviora Dialogue afzalliklari/i)).toBeInTheDocument();
    expect(screen.getByText(/Tez-tez beriladigan/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Aviora Dialogue nima\?/i })).toBeInTheDocument();
  });
});
