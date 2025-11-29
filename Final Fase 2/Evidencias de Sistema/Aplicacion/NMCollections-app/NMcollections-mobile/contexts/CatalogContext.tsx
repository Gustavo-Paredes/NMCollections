import React, { createContext, useState, useContext, ReactNode } from 'react';

export interface Product {
  id: number;
  nombre: string;
  precio: number;
  imagen: string;
  // ...otros campos
}

interface CatalogContextType {
  products: Product[];
  setProducts: (products: Product[]) => void;
}

const CatalogContext = createContext<CatalogContextType | undefined>(undefined);

export const useCatalog = () => {
  const context = useContext(CatalogContext);
  if (!context) throw new Error('useCatalog must be used within CatalogProvider');
  return context;
};

export const CatalogProvider = ({ children }: { children: ReactNode }) => {
  const [products, setProducts] = useState<Product[]>([]);
  return (
    <CatalogContext.Provider value={{ products, setProducts }}>
      {children}
    </CatalogContext.Provider>
  );
};
