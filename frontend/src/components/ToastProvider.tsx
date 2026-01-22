/**
 * Toast notification provider with custom styling.
 */
import { Toaster } from 'react-hot-toast';

export default function ToastProvider() {
  return (
    <Toaster
      position="bottom-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#fff',
          color: '#1F2937',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: '500',
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
          border: '1px solid #E5E7EB',
        },
        success: {
          duration: 4000,
          iconTheme: {
            primary: '#059669',
            secondary: '#ECFDF5',
          },
          style: {
            background: '#ECFDF5',
            color: '#065F46',
            border: '1px solid #A7F3D0',
          },
        },
        error: {
          duration: 6000,
          iconTheme: {
            primary: '#DC2626',
            secondary: '#FFF1F2',
          },
          style: {
            background: '#FFF1F2',
            color: '#991B1B',
            border: '1px solid #FECDD3',
          },
        },
        loading: {
          iconTheme: {
            primary: '#6366F1',
            secondary: '#EEF2FF',
          },
          style: {
            background: '#EEF2FF',
            color: '#4338CA',
            border: '1px solid #C7D2FE',
          },
        },
      }}
    />
  );
}
