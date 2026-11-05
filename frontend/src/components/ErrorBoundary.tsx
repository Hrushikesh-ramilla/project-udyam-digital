import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught frontend error caught by ErrorBoundary:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-slate-100">
          <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl text-center space-y-4">
            <div className="w-12 h-12 bg-red-600/20 text-red-500 rounded-2xl flex items-center justify-center mx-auto border border-red-500/30">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">System Recovered Safely</h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              An unexpected UI state occurred. Project Udyam Digital's error boundary prevented a browser crash.
            </p>
            {this.state.error && (
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-[11px] font-mono text-red-400 text-left overflow-x-auto max-h-32">
                {this.state.error.message || String(this.state.error)}
              </div>
            )}
            <button
              onClick={this.handleReset}
              className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 text-white font-bold py-2.5 px-4 rounded-xl text-xs shadow-lg shadow-red-600/30 transition-all"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Reset &amp; Reload Application</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
