import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { App } from "./App";

describe("App", () => {
  test("renders the product landing page with primary sections", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /Ethical Dialogue AI/i })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /Sign in/i })[0]).toHaveAttribute("href", "/signin");
    expect(screen.getByText(/Consent-first automation/i)).toBeInTheDocument();
    expect(screen.getByText(/Telegram conversations/i)).toBeInTheDocument();
    expect(screen.getByText(/Human approval/i)).toBeInTheDocument();
  });
});
