import { Component, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { error: Error | null };

/** Shows why the town failed (no WebGL, a model that wouldn't load) instead of a blank page. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="load-error" role="alert">
        <h2>The town couldn't load</h2>
        <p>{this.state.error.message}</p>
        <p>Try a recent version of Chrome, Edge, Firefox or Safari with hardware acceleration turned on.</p>
      </div>
    );
  }
}
