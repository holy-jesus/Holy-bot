import React from 'react';

export interface UserProfile {
  username: string;
  avatarUrl: string;
  isMod: boolean;
}

export interface StatMetric {
  label: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
}

export interface Timer {
  id: string;
  name: string;
  interval: number; // minutes
  message: string;
  active: boolean;
}

export interface Moderator {
  id: string;
  username: string;
  addedAt: string;
  permissions: string[];
}

export enum BotStatus {
  ONLINE = 'Online',
  OFFLINE = 'Offline',
  MAINTENANCE = 'Maintenance'
}

// Command Types
export type CommandMode = 'basic' | 'advanced' | 'ai';

export interface Command {
  id: string;
  name: string;
  mode: CommandMode;
  active: boolean;
  cooldown: number; // seconds
  // Basic Mode
  trigger?: string;
  response?: string;
  // AI Mode
  aiPrompt?: string;
  // Advanced Mode (JSON stringified flow data)
  flowData?: any; 
}