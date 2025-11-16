export interface Node {
  id: string
  name: string
  type: "current" | "predicted"
  probability: number
  x?: number
  y?: number
  fx?: number
  fy?: number
}

export interface Link {
  source: string | Node
  target: string | Node
  probability: number
}

export const mockAttackGraphData = {
  nodes: [
    {
      id: "T1190",
      name: "Exploit Public-Facing Application",
      type: "current",
      probability: 1.0,
    },
    {
      id: "T1133",
      name: "External Remote Services",
      type: "predicted",
      probability: 0.92,
    },
    {
      id: "T1078",
      name: "Valid Accounts",
      type: "predicted",
      probability: 0.85,
    },
    {
      id: "T1059",
      name: "Command and Scripting Interpreter",
      type: "predicted",
      probability: 0.78,
    },
    {
      id: "T1486",
      name: "Data Encrypted for Impact",
      type: "predicted",
      probability: 0.68,
    },
    {
      id: "T1565",
      name: "Data Manipulation",
      type: "predicted",
      probability: 0.58,
    },
  ],
  links: [
    { source: "T1190", target: "T1133", probability: 0.92 },
    { source: "T1190", target: "T1078", probability: 0.85 },
    { source: "T1133", target: "T1059", probability: 0.8 },
    { source: "T1078", target: "T1059", probability: 0.75 },
    { source: "T1059", target: "T1486", probability: 0.68 },
    { source: "T1059", target: "T1565", probability: 0.58 },
  ],
}

import type { TechniqueDetails } from '@/lib/api-client'

export const mockTechniqueDetails: Record<string, TechniqueDetails> = {
  T1190: {
    id: "T1190",
    name: "Exploit Public-Facing Application",
    description:
      "Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program using software, data, or commands in order to cause unintended or unanticipated behavior.",
    detection:
      "Monitor application logs for unusual patterns, failed authentication attempts, and unexpected connections from external IPs.",
    mitigation:
      "Apply patches and security updates regularly. Use intrusion prevention systems. Implement web application firewalls.",
    platforms: ["Linux", "Windows", "macOS", "SaaS"],
    tactics: ["Initial Access"],
  },
  T1133: {
    id: "T1133",
    name: "External Remote Services",
    description:
      "Adversaries may leverage external-facing remote services to initially access and/or persist within a network.",
    detection:
      "Monitor for unexpected remote service access, unusual authentication from external sources, and VPN anomalies.",
    mitigation:
      "Restrict access to remote services. Implement MFA. Use VPN with strong encryption. Monitor service logs.",
    platforms: ["Linux", "Windows", "macOS"],
    tactics: ["Initial Access", "Persistence"],
  },
  T1078: {
    id: "T1078",
    name: "Valid Accounts",
    description:
      "Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion.",
    detection:
      "Monitor for unusual account activity, impossible travel scenarios, access from new locations, and failed MFA attempts.",
    mitigation: "Enforce strong passwords and MFA. Implement conditional access policies. Monitor account activities.",
    platforms: ["Linux", "Windows", "macOS", "SaaS"],
    tactics: ["Defense Evasion", "Persistence", "Privilege Escalation", "Initial Access"],
  },
  T1059: {
    id: "T1059",
    name: "Command and Scripting Interpreter",
    description:
      "Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries. These interfaces and languages provide ways to interact with computer systems.",
    detection:
      "Monitor command execution, script execution logs, and PowerShell/bash activity. Alert on suspicious commands.",
    mitigation: "Disable command interpreters when possible. Use application whitelisting. Monitor command execution.",
    platforms: ["Linux", "Windows", "macOS"],
    tactics: ["Execution"],
  },
  T1486: {
    id: "T1486",
    name: "Data Encrypted for Impact",
    description:
      "Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources.",
    detection: "Monitor for mass file encryption, unusual disk activity, file extensions changes, and ransom notes.",
    mitigation: "Backup important data. Use endpoint protection. Monitor file system activity. Segment networks.",
    platforms: ["Linux", "Windows", "macOS"],
    tactics: ["Impact"],
  },
  T1565: {
    id: "T1565",
    name: "Data Manipulation",
    description:
      "Adversaries may insert, delete, or manipulate data in order to influence external outcomes or hide activity, thus delegitimizing the integrity of the system.",
    detection: "Monitor database access patterns, data modification logs, and unusual query execution.",
    mitigation: "Implement data integrity checks. Use access controls and audit logs. Monitor data changes.",
    platforms: ["Linux", "Windows", "macOS"],
    tactics: ["Impact"],
  },
}
