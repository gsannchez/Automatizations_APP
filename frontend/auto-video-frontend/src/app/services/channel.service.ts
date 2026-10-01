import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiClientService } from '../core/services/api-client.service';

export interface Channel {
  id: number;
  name: string;
  platform: string;
  description?: string;
  is_active?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ChannelService {
  private readonly http = inject(HttpClient);
  private readonly api = inject(ApiClientService);

  getChannels(): Observable<Channel[]> {
    return this.http.get<Channel[]>(this.api.url('/channels'));
  }

  createChannel(channel: Partial<Channel>): Observable<Channel> {
    return this.http.post<Channel>(this.api.url('/channels'), channel);
  }

  deleteChannel(id: number): Observable<void> {
    return this.http.delete<void>(this.api.url(`/channels/${id}`));
  }
}
