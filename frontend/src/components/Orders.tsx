import { useCallback, useEffect, useState } from "react";

import { api } from "../api";
import { toast } from "../toast";
import type { Order, OrderPage } from "../types";

const PAGE_SIZE = 10;
const STATUSES = ["pending", "completed", "cancelled"] as const;

export default function Orders({ isAuthed }: { isAuthed: boolean }) {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);

  const load = useCallback(async () => {
    const query = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
    if (status) query.set("status", status);
    try {
      const res = await api<OrderPage>(`/api/orders?${query}`);
      setOrders(res.orders);
      setTotal(res.total_count);
    } catch (err) {
      toast((err as Error).message);
    }
  }, [page, status]);

  useEffect(() => {
    void load();
  }, [load]);

  const updateStatus = async (id: number, next: string) => {
    try {
      await api(`/api/orders/${id}`, { method: "POST", body: JSON.stringify({ status: next }) });
      toast(`Order #${id} → ${next}`);
    } catch (err) {
      toast((err as Error).message);
    } finally {
      await load();
    }
  };

  const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <section className="card">
      <div className="card-head">
        <h2>Orders</h2>
        <div className="filters">
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All statuses</option>
            {STATUSES.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <div className="pager">
            <button
              className="btn btn-ghost"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
            >
              ‹
            </button>
            <span className="muted">{page}</span>
            <button
              className="btn btn-ghost"
              onClick={() => setPage(page + 1)}
              disabled={page >= lastPage}
            >
              ›
            </button>
          </div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Customer</th>
            <th>Amount</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id}>
              <td>{order.id}</td>
              <td>{order.customer_id}</td>
              <td>${Number(order.total_amount).toFixed(2)}</td>
              <td>
                <span className={`badge ${order.status}`}>{order.status}</span>
              </td>
              <td>
                <select
                  value={order.status}
                  disabled={!isAuthed}
                  onChange={(e) => updateStatus(order.id, e.target.value)}
                >
                  {STATUSES.map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {orders.length === 0 && <p className="muted">No orders match this filter.</p>}
      <p className="muted small">
        {total} order{total === 1 ? "" : "s"} total
      </p>
    </section>
  );
}
