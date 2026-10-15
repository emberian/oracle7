# Oracle7 Embedded Systems & Microcontrollers (#59, tier B)

**id** `embedded` - organ `organ_embedded_v1.EmbeddedOrgan` composed in front of the frozen head `oracle_release_runtime_w503`.

## Verdict

- decision: **ADMIT** (gate v2)
- held-out domain: specialist 25/25 (false yes 0) vs head 1/25 (false yes 0)
- core capability panel: head 160 -> composed 160 (0 items swept in by the full sweep)
- reasons: none

## Sources and licences

- Arduino documentation (timers, Serial / UART framing) (CC-BY-SA 3.0 (store ships share-alike)) https://docs.arduino.cc/
- AVR timer CTC relation f = f_clk / (N (1 + OCR)) and UBRR = f_clk / (16 baud) - 1 (Microchip ATmega328P datasheet formulas) (facts) https://www.microchip.com/en-us/product/ATmega328P

## What it takes

- answers: tick, tick_freq, overflow, overflow_freq, ctc, uart_time, uart_throughput, ubrr, address_space, address_bytes
- declines (in-domain): impossible
- everything else falls through to the head unchanged

## Notes and known gaps

AVR conventions named (CTC, UBRR normal asynchronous mode); UART 8N1 unless stated. A CTC value that does not fit the timer is declined with the reason (use a larger prescaler). Narrowed from the start (narrow_v1); NO numbers rule (LAW 2026-09-29).
