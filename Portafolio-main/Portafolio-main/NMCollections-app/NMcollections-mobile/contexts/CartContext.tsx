import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Product } from '../screens/screen-cli/CatalogScreen';

export interface CartItem {
  product: Product;
  quantity: number;
}

interface CartContextType {
  cart: CartItem[];
  addToCart: (product: Product) => void;
  removeFromCart: (id: number) => void;
  increment: (id: number) => void;
  decrement: (id: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);

  function addToCart(product: Product) {
    setCart(prev => {
      const idx = prev.findIndex(item => item.product.id === product.id);
      if (idx !== -1) {
        // Si ya existe, aumenta cantidad
        const updated = [...prev];
        updated[idx].quantity += 1;
        return updated;
      }
      return [...prev, { product, quantity: 1 }];
    });
  }
  function removeFromCart(id: number) {
    setCart(prev => prev.filter(item => item.product.id !== id));
  }
  function increment(id: number) {
    setCart(prev => prev.map(item => item.product.id === id ? { ...item, quantity: item.quantity + 1 } : item));
  }
  function decrement(id: number) {
    setCart(prev => prev.map(item => item.product.id === id ? { ...item, quantity: Math.max(1, item.quantity - 1) } : item));
  }
  function clearCart() {
    setCart([]);
  }

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, increment, decrement, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) throw new Error('useCart must be used within a CartProvider');
  return context;
}
