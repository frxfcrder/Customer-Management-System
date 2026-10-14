import { useEffect, useState } from "react";

import { api } from "../api";
import { toast } from "../toast";
import type { CategoryList } from "../types";

export default function Categories() {
  const [categories, setCategories] = useState<CategoryList["categories"]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api<CategoryList>("/api/categories")
      .then((res) => setCategories(res.categories))
      .catch((err: Error) => toast(err.message))
      .finally(() => setLoaded(true));
  }, []);

  return (
    <section className="card">
      <h2>Categories</h2>
      <div className="cards">
        {categories.map((category) => (
          <div key={category.id} className="tiles">
            <h4>{category.name}</h4>
            <p className="muted small">{category.description || "No description"}</p>
          </div>
        ))}
      </div>
      {loaded && categories.length === 0 && <p className="muted">No categories defined.</p>}
    </section>
  );
}
