import { useQuery } from "@tanstack/react-query";

import { Card } from "../components/ui/Card";
import { api } from "../services/api";

export function ProductsPage() {
  const products = useQuery({ queryKey: ["products"], queryFn: api.products });
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Products</h1>
      <div className="grid gap-4 lg:grid-cols-2">
        {products.data?.results.map((product) => (
          <Card key={String(product.id)}>
            <h2 className="font-semibold">{String(product.name)}</h2>
            <p className="mt-2 text-sm text-slate-600">{String(product.short_description)}</p>
            <p className="mt-3 text-sm">From {String(product.starting_price)} {String(product.currency)}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
