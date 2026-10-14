import { useCallback, useEffect, useState, type FormEvent } from "react";

import { api } from "../api";
import { toast } from "../toast";
import type { Customer, CustomerPage, Order } from "../types";

const PAGE_SIZE = 10;

interface DetailState {
  customer: Customer;
  orders: Order[];
}

const emptyForm = { id: null as number | null, name: "", email: "", phone: "" };

export default function Customers({ isAuthed }: { isAuthed: boolean }) {
  const [page, setPage] = useState(1);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState<DetailState | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await api<CustomerPage>(`/api/customers?page=${page}&page_size=${PAGE_SIZE}`);
      setCustomers(res.data);
      setTotal(res.total_count);
    } catch (err) {
      toast((err as Error).message);
    }
  }, [page]);

  useEffect(() => {
    void load();
  }, [load]);

  const openDetail = async (id: number) => {
    try {
      const [customer, ordersRes] = await Promise.all([
        api<Customer>(`/api/customers/${id}`),
        api<{ orders: Order[]; count: number }>(`/api/customers/${id}/orders`),
      ]);
      setDetail({ customer, orders: ordersRes.orders });
      setForm({
        id: customer.id,
        name: customer.name,
        email: customer.email,
        phone: customer.phone ?? "",
      });
    } catch (err) {
      toast((err as Error).message);
    }
  };

  const resetForm = () => {
    setForm(emptyForm);
    setError("");
  };

  const closeDetail = () => {
    setDetail(null);
    resetForm();
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim() || null,
    };

    try {
      if (form.id) {
        await api(`/api/customers/${form.id}`, { method: "POST", body: JSON.stringify(payload) });
        toast("Customer updated");
      } else {
        await api("/api/customers", { method: "POST", body: JSON.stringify(payload) });
        toast("Customer created");
      }
      const editedId = form.id;
      resetForm();
      await load();
      if (editedId) await openDetail(editedId);
      else setDetail(null);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <>
      <div className="grid-2">
        <div className="card">
          <h2>{form.id ? `Edit customer #${form.id}` : "New customer"}</h2>
          <form onSubmit={submit}>
            <label>
              Name
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Jane Doe"
                required
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="jane@example.com"
                required
              />
            </label>
            <label>
              Phone
              <input
                type="text"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="555-0100"
              />
            </label>
            <div className="row">
              <button className="btn btn-primary" type="submit" disabled={!isAuthed}>
                Save
              </button>
              {form.id && (
                <button className="btn btn-ghost" type="button" onClick={closeDetail}>
                  Cancel
                </button>
              )}
            </div>
            {!isAuthed && <p className="muted small">Log in to create or edit customers.</p>}
            {error && <p className="error">{error}</p>}
          </form>
        </div>

        <div className="card">
          <div className="card-head">
            <h2>Customers</h2>
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
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id} className="clickable" onClick={() => openDetail(customer.id)}>
                  <td>{customer.name}</td>
                  <td>{customer.email}</td>
                  <td>{customer.phone || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {customers.length === 0 && <p className="muted">No customers yet.</p>}
          <p className="muted small">
            {total} customer{total === 1 ? "" : "s"} total
          </p>
        </div>
      </div>

      {detail && (
        <div className="card">
          <div className="card-head">
            <h2>{detail.customer.name}</h2>
            <button className="btn btn-ghost" onClick={closeDetail}>
              Close
            </button>
          </div>
          <p className="muted">
            {detail.customer.email} · {detail.customer.phone || "no phone"} · joined{" "}
            {String(detail.customer.created_at).slice(0, 10)}
          </p>
          <h3>Orders</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {detail.orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>${Number(order.total_amount).toFixed(2)}</td>
                  <td>
                    <span className={`badge ${order.status}`}>{order.status}</span>
                  </td>
                  <td>{String(order.created_at).slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {detail.orders.length === 0 && (
            <p className="muted small">No orders for this customer.</p>
          )}
        </div>
      )}
    </>
  );
}
