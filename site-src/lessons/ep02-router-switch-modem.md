---
ep: 02
slug: router-vs-switch-vs-modem
title: Router vs switch vs modem
series: Network Bytes
series_blurb: Networking from zero, one minute at a time. Follows the Cisco CCNA 200-301 exam topics.
topic: CCNA 1.1
date: 2026-10-11
summary: That "router" on your shelf is usually three devices in a trench coat. Here's what each one does.
video: 2026-10-11-ep02/video.mp4
poster: 2026-10-11-ep02/thumbnail.png
instagram: https://www.instagram.com/reel/DeVjZK_KUiw/
---
> **In one bite:** the **modem** connects your home to your internet provider, the **switch** connects the devices inside your home, and the **router** connects your home network to other networks and decides where traffic goes. Most home boxes do all three, plus Wi-Fi.

## One box, three jobs

The box your internet provider gave you probably says "router" or "gateway" on it. Inside, it's usually doing three different jobs that used to be three separate devices. Let's take them one at a time, following your data from the wall to your laptop.

## The modem: a translator

Your internet provider sends its signal into your home over a cable TV line, a phone line or a fiber line. That signal isn't in a form your laptop understands. The **modem** translates between the two: it turns the provider's signal into normal network data, and back again for anything you send out.

Without a modem, your home network has no way to talk to your provider, so it has no way to reach the internet.

## The switch: connects devices inside

A **switch** connects the devices inside one network to each other. When data arrives for your TV, the switch sends it to the TV only, not to every device in the house. That keeps things fast and tidy.

If you've ever seen a box with a row of identical network ports on the back, that's a switch at work. On a home box, the numbered LAN ports are its built-in switch.

## The router: connects networks

A **router** sits on the border between two networks, like your home and the internet, and decides where each piece of traffic should go next. Is this data for the laptop in the kitchen, or for a server in another country? The router makes that call, over and over, for every packet.

Here's the easy way to keep them apart:

- A **switch** connects **devices** in the same network.
- A **router** connects **networks** to other networks.

## And Wi-Fi?

Most home boxes also have a **wireless access point** built in. That's the part that lets phones and laptops join the network without a cable. It's another job squeezed into the same box.

## In an office, they split up

In a business, these jobs are usually done by separate, more powerful devices that sit in a rack: a router at the edge, switches connecting the desks, and access points on the ceilings. Those are the devices network engineers (and CCNA students) spend most of their time with.

## Try it yourself

Look at the back of your home internet box. You'll usually find one port that's a different color or labeled **WAN** or **Internet**. That's where the outside world comes in. The group of matching ports labeled **LAN** or numbered 1 to 4 is the built-in switch for your wired devices.

## Common mix-up

Wi-Fi and the internet aren't the same thing. Wi-Fi is just a wireless way to join your home network. If your modem loses its connection to the provider, your phone can still show full Wi-Fi bars and have no internet at all.

## Sources

- Cloudflare Learning Center, ["What is a router?"](https://www.cloudflare.com/learning/network-layer/what-is-a-router/): routers connect networks; modems connect them to the internet
- Cloudflare Learning Center, ["What is a network switch?"](https://www.cloudflare.com/learning/network-layer/what-is-a-network-switch/): a switch sends data only to the device it's meant for
- Cisco, ["What is a switch vs a router?"](https://www.cisco.com/site/us/en/learn/topics/small-business/network-switch-vs-router.html): switches connect devices, routers connect networks and provide internet access
- CableLabs, ["A 101 on DOCSIS Technology"](https://www.cablelabs.com/blog/a-101-on-docsis-technology-the-heart-of-cable-broadband): the cable modem translates the provider's signal
- Cisco, [CCNA 200-301 v1.1 exam topics](https://learningcontent.cisco.com/documents/marketing/exam-topics/200-301-CCNA-v1.1.pdf): 1.1 routers, switches and access points
