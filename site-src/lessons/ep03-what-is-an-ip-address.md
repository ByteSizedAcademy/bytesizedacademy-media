---
ep: 03
slug: what-is-an-ip-address
title: What is an IP address?
series: Network Bytes
series_blurb: Networking from zero, one minute at a time. Follows the Cisco CCNA 200-301 exam topics.
topic: CCNA 1.6
date: 2026-10-11
summary: Every device online has an address, just like your house. Here's how to read one.
video: 2026-10-11-ep03/video.mp4
poster: 2026-10-11-ep03/thumbnail.png
instagram: https://www.instagram.com/reel/DeXFAclkos5/
next_title: What is a MAC address?
---
> **In one bite:** an IP address tells the network where to deliver data, the way a street address tells the mail carrier where to drop off a letter. A common kind looks like `192.168.1.25`.

## An address for every device

Every device that talks on a network needs an address, so data sent to it ends up in the right place. On networks and the internet, that's the **IP address** (IP stands for Internet Protocol, the set of rules for addressing and delivering data).

Think of the mail. A letter without an address can't be delivered. Data is the same: no address, no delivery.

## How to read one

The most common kind, called **IPv4**, is written as four numbers separated by dots:

`192.168.1.25`

Each of the four numbers can be anything from **0 to 255**. Why 255? Behind the scenes an IPv4 address is 32 bits (ones and zeros), split into four groups of 8 bits. Eight bits can count 256 different values, from 0 up to 255.

The address has two parts:

- The first part names the **network**, like the street. In `192.168.1.25`, that's usually `192.168.1`.
- The last part names the **device** on that network, like the house number. Here, that's `25`.

Every device on the same home network shares the "street" part and gets its own "house number."

## Where do addresses come from?

You almost never type one in yourself. When your phone joins your Wi-Fi, your router hands it an address automatically and remembers it for a while. That's called a **lease**. Leave home and come back tomorrow, and your phone may get a different address. Addresses handed out this way are called **dynamic**. Addresses that are set by hand and never change, which servers and printers often use, are called **static**.

## Try it yourself

Open your phone's Wi-Fi settings and tap the network you're connected to. Look for **IP address**. It will probably start with `192.168` or `10.`, which are ranges set aside for home and office networks. Why those numbers show up everywhere is a whole lesson of its own, coming soon in this series.

## Good to know

- This lesson covers **IPv4**. There's a newer, much longer kind of address called **IPv6**, made because the world was running out of IPv4 addresses. It gets its own episode later in the series.
- "First part network, last part device" is a simplification. The exact split is set by something called a **subnet mask**, which we'll cover when we get to subnetting.
- The automatic hand-out is done by a service called **DHCP**, which also gets its own episode.

## For CCNA learners

This lines up with CCNA 200-301 exam topic **1.6, configure and verify IPv4 addressing and subnetting**. For now, get comfortable reading an address as four numbers from 0 to 255, with a network part and a device part.

## Sources

- Cloudflare Learning Center, ["What is my IP address?"](https://www.cloudflare.com/learning/dns/glossary/what-is-my-ip-address/): IP addresses identify devices online; IPv4 is four numbers separated by dots; dynamic addresses are temporary
- IETF, [RFC 791, "Internet Protocol"](https://datatracker.ietf.org/doc/html/rfc791): IPv4 addresses are 32 bits, written as four 8-bit numbers from 0 to 255
- Microsoft Learn, ["What is DHCP?"](https://learn.microsoft.com/en-us/windows-server/networking/technologies/dhcp/dhcp-top): addresses are handed out automatically and leased, so they can change
- Cisco, [CCNA 200-301 v1.1 exam topics](https://learningcontent.cisco.com/documents/marketing/exam-topics/200-301-CCNA-v1.1.pdf): 1.6 configure and verify IPv4 addressing
