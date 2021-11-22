# Candy Home Assistant component

[![Run tests](https://github.com/ofalvai/home-assistant-candy/actions/workflows/test.yml/badge.svg)](https://github.com/ofalvai/home-assistant-candy/actions/workflows/test.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![codecov](https://codecov.io/gh/ofalvai/home-assistant-candy/branch/main/graph/badge.svg?token=HE0AIQOGAD)](https://codecov.io/gh/ofalvai/home-assistant-candy)

Custom component for [Home Assistant](https://homeassistant.io) that integrates Candy/Haier/Simply-Fi home appliances.


## Features
- Supported appliances:
   - washing machine 
   - tumble dryer
   - oven
   - dishwasher
- Uses the local API and its status endpoint
- Creates various sensors, such as device state and remaining time. Everything else is exposed as sensor attributes

## Installation

1. Install [HACS](https://hacs.xyz/)
2. Go to the integrations list in HACS and search for `Candy Simply-Fi`
4. Restart Home Assistant
5. Go to the Integrations page, click Add integrations and select `Candy`
6. Complete the config flow

## Configuration

You need the IP address of the machine and the encryption key. This can be guessed with [CandySimplyFi-tool](https://github.com/MelvinGr/CandySimplyFi-tool).


## My device isn't supported. Can you help?

Yes. If you have an appliance that is not supported yet, or you see an error, head over to the [Discussions section](https://github.com/ofalvai/home-assistant-candy/discussions/categories/device-support-improvements). Open a new thread or comment to an existing one with the following information:

- The status API response of your device (use [CandySimplyFi-tool](https://github.com/MelvinGr/CandySimplyFi-tool) to get the JSON)
- A brief explanation of what each field means in the response and how it changes based on the device state, eg. _The `SpinSp` field is probably the spin speed divided by 100, I have seen values 6, 8, 10 and 12 in the response_
