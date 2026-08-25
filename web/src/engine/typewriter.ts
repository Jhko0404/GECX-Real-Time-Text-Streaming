export class AdaptiveTypewriterEngine {
  private queue: string[] = [];
  private renderedText: string = "";
  private isRunning: boolean = false;
  private onUpdate: (text: string) => void;
  private onComplete: () => void;
  private timerId: any = null;
  private isFirstChunk: boolean = true;

  constructor(onUpdate: (text: string) => void, onComplete: () => void) {
    this.onUpdate = onUpdate;
    this.onComplete = onComplete;
  }

  public pushChunk(chunk: string): void {
    // Hyper-TTFT: If first chunk, immediately render it with 0ms delay
    if (this.isFirstChunk) {
      this.isFirstChunk = false;
      this.renderedText += chunk;
      this.onUpdate(this.renderedText);
      return;
    }

    const chars = Array.from(chunk);
    this.queue.push(...chars);
    if (!this.isRunning) {
      this.isRunning = true;
      this.tick();
    }
  }

  private tick(): void {
    if (this.queue.length === 0) {
      this.isRunning = false;
      this.onComplete();
      return;
    }

    const nextChar = this.queue.shift()!;
    this.renderedText += nextChar;
    this.onUpdate(this.renderedText);

    // Fast 15ms adaptive delay with aggressive backlog speed-up
    const backlog = Math.max(0, this.queue.length - 8);
    const delay = Math.max(3, Math.floor(15 / (1 + 0.12 * backlog)));

    this.timerId = setTimeout(() => this.tick(), delay);
  }

  public flush(): void {
    if (this.timerId) clearTimeout(this.timerId);
    while (this.queue.length > 0) {
      this.renderedText += this.queue.shift()!;
    }
    this.onUpdate(this.renderedText);
    this.isRunning = false;
    this.onComplete();
  }

  public reset(): void {
    if (this.timerId) clearTimeout(this.timerId);
    this.queue = [];
    this.renderedText = "";
    this.isRunning = false;
    this.isFirstChunk = true;
  }
}
