import React from "react";

interface Props {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  confirmColor = "bg-red-600 hover:bg-red-700",
  onConfirm,
  onCancel,
}: Props) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-md w-full p-6 shadow-2xl">
        <div className="flex items-start gap-4 mb-6">
          <div className="flex-shrink-0 w-12 h-12 bg-red-950 rounded-full flex items-center justify-center">
            <span className="text-2xl">⚠️</span>
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
            <p className="text-gray-400 text-sm">{message}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onConfirm}
            className={`flex-1 ${confirmColor} text-white py-2.5 rounded-lg font-medium transition-colors`}
          >
            {confirmText}
          </button>
          <button
            onClick={onCancel}
            className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2.5 rounded-lg font-medium transition-colors"
          >
            {cancelText}
          </button>
        </div>
      </div>
    </div>
  );
}