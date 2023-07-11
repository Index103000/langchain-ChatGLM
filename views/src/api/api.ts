import request from './axios'
export const api = async (data: object): Promise<any> => {
  return await request({
    ...data,
  })
}

export const apiStream = async (data: object, controller?: AbortController, onMessage?: Function, onAbortController?: Function, onError?: Function): Promise<any> => {
  try {
    const res = await fetch(data.url, {
      method: data.method,
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller?.signal,
      body: data.data,
    });

    if (res.ok) {
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let responseText = '';

      while (true) {
        const { value: chunk, done } = await reader?.read();

        if (done) {
          onMessage?.(responseText, true);
          break;
        }

        responseText += decoder.decode(chunk);
        onMessage?.(responseText, false);
      }
    } else {
      onError?.(new Error('Stream Error'), res.status);
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      onAbortController?.();
    } else {
      onError?.(err as Error, 'Network Error');
    }
  }
};
