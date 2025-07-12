import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import autoprefixer from 'autoprefixer';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isProd = mode === 'production';
  
  return {
    plugins: [react()],
    
    server: {
      allowedHosts: true,
      port: 3000,
      open: true
    },
    
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
      extensions: ['.mjs', '.js', '.jsx', '.ts', '.tsx', '.json']
    },
    
    optimizeDeps: {
      esbuildOptions: {
        loader: {
          '.js': 'jsx',
        },
      },
    },
    
    build: {
      // Optimize build
      target: 'es2020',
      outDir: 'dist',
      assetsDir: 'assets',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: isProd,
          drop_debugger: isProd
        }
      },
      
      // Split chunks for better caching
      rollupOptions: {
        output: {
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'ui-components': [
              '@radix-ui/react-accordion',
              '@radix-ui/react-alert-dialog',
              '@radix-ui/react-avatar',
              '@radix-ui/react-checkbox',
              '@radix-ui/react-dialog',
              '@radix-ui/react-dropdown-menu',
              '@radix-ui/react-label',
              '@radix-ui/react-popover',
              '@radix-ui/react-select',
              '@radix-ui/react-tabs'
            ],
            'form-utils': ['react-hook-form', '@hookform/resolvers', 'zod'],
            'data-viz': ['recharts'],
            'utils': ['date-fns', 'clsx', 'tailwind-merge']
          }
        }
      },
      
      // Generate sourcemaps for production
      sourcemap: !isProd,
      
      // Reduce chunk size warnings threshold
      chunkSizeWarningLimit: 1000
    },
    
    // CSS optimization
    css: {
      devSourcemap: true,
      postcss: {
        plugins: [
          autoprefixer
        ]
      }
    },
    
  };
});
