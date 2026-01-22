/**
 * Toast notification utility functions.
 */
import toast from 'react-hot-toast';

/**
 * Show a success toast notification.
 */
export const showSuccess = (message: string) => {
  toast.success(message, {
    duration: 4000,
  });
};

/**
 * Show an error toast notification.
 */
export const showError = (message: string) => {
  toast.error(message, {
    duration: 6000,
  });
};

/**
 * Show a warning/info toast notification.
 */
export const showWarning = (message: string) => {
  toast(message, {
    duration: 5000,
    icon: '⚠️',
    style: {
      background: '#FFFBEB',
      color: '#92400E',
      border: '1px solid #FDE68A',
    },
  });
};

/**
 * Show a loading toast and return the toast ID for later dismissal.
 */
export const showLoading = (message: string) => {
  return toast.loading(message);
};

/**
 * Dismiss a specific toast by ID.
 */
export const dismissToast = (toastId: string) => {
  toast.dismiss(toastId);
};

/**
 * Show a custom confirmation toast for delete operations.
 * 
 * @param itemType - Type of item being deleted (e.g., 'task', 'project', 'tag')
 * @param itemName - Name of the specific item being deleted
 * @param onConfirm - Callback to execute if user confirms
 */
export const showDeleteConfirm = (
  itemType: string,
  itemName: string,
  onConfirm: () => Promise<void>
) => {
  toast(
    (t) => (
      <div className="flex flex-col gap-3">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center">
            <svg
              className="w-5 h-5 text-rose-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">
              Delete {itemType}?
            </h3>
            <p className="text-sm text-gray-600">
              Are you sure you want to delete <span className="font-medium">"{itemName}"</span>?
              {itemType === 'project' && ' This won\'t delete its tasks.'}
              {itemType === 'tag' && ' This will remove it from all tasks.'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={async () => {
              toast.dismiss(t.id);
              const loadingToast = showLoading(`Deleting ${itemType}...`);
              try {
                await onConfirm();
                dismissToast(loadingToast);
                showSuccess(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully`);
              } catch (error) {
                dismissToast(loadingToast);
                showError(`Failed to delete ${itemType}`);
              }
            }}
            className="flex-1 bg-rose-600 hover:bg-rose-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
          >
            Delete
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    ),
    {
      duration: Infinity,
      style: {
        background: '#fff',
        border: '2px solid #FCA5A5',
        padding: '16px',
        minWidth: '400px',
        maxWidth: '500px',
      },
    }
  );
};

/**
 * Show a generic confirmation toast.
 * 
 * @param message - Confirmation message to display
 * @param onConfirm - Callback to execute if user confirms
 * @param confirmText - Text for confirm button (default: 'Confirm')
 * @param cancelText - Text for cancel button (default: 'Cancel')
 */
export const showConfirm = (
  message: string,
  onConfirm: () => void | Promise<void>,
  confirmText: string = 'Confirm',
  cancelText: string = 'Cancel'
) => {
  toast(
    (t) => (
      <div className="flex flex-col gap-3">
        <p className="text-gray-900">{message}</p>
        <div className="flex gap-2">
          <button
            onClick={async () => {
              toast.dismiss(t.id);
              await onConfirm();
            }}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
          >
            {confirmText}
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors text-sm"
          >
            {cancelText}
          </button>
        </div>
      </div>
    ),
    {
      duration: Infinity,
      style: {
        background: '#fff',
        border: '2px solid #FCD34D',
        padding: '16px',
        minWidth: '350px',
      },
    }
  );
};
