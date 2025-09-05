import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow external connections
    // port: 5173, // Let Vite choose the port automatically
    allowedHosts: [
      '.trycloudflare.com', // Allow ANY trycloudflare.com subdomain
      'localhost',
      '127.0.0.1'
    ],
    proxy: {
      // Proxy API calls to backend during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // Enable source maps for debugging
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  define: {
    // Define global constants  
    __DEV__: JSON.stringify(true) // Development mode
  }
})
