export interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: number;
  customer_id: number;
  total_amount: number;
  status: string;
  payment_status: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CustomerPage {
  data: Customer[];
  total_count: number;
  page: number;
  size: number;
}

export interface OrderPage {
  orders: Order[];
  total_count: number;
  page: number;
  page_size: number;
}

export interface CategoryList {
  categories: Category[];
  count: number;
}

export interface Session {
  token: string;
  email: string;
}
