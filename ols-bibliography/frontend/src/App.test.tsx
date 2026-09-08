import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders navigation links', () => {
    render(<App />);
    expect(screen.getByText(/OLS Bibliographie/i)).toBeInTheDocument();
    expect(screen.getByText(/Recherche/i)).toBeInTheDocument();
    expect(screen.getByText(/Bibliothèques/i)).toBeInTheDocument();
    expect(screen.getByText(/Veilles/i)).toBeInTheDocument();
  });
});
