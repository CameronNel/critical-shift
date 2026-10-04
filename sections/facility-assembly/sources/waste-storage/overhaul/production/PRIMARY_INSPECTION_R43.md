# Primary actual pixel inspection — R43

Last full scored baseline R39. Expanded PASS574661tri/328new+57inheritedsupports; zero protected changes/issues. Own cold not started. Targeted pixel review in progress.

| View | Individually opened actual pixel observation |
|---|---|
| W10_ResidueService | Three closed residue overpacks and clearly separate solid lifting ends remain; no pipe circuit ambiguity or route regression. |
| C02_Casks | Dominant large coating stamps removed and colors shift, but the broad cask faces remain largely uniform. Solid trunnions and process geometry clear. |
| W04_CellService | Big stamps absent, independent trunnion ends intact, but broad painted shell remains uniform. |
| C06_Dry | Lid/front side remain uniform despite intended broad handled fields. |
| C07_Quarantine | Brown broad face remains uniform, closure and contained filter intact. |

Primary opened W10/C02/W04/C06/C07 individually. Read-only shader probe identifies the reason intended fields fail: coating_history connected the disabled Vector output of a LENGTH node instead of its enabled Value output, flattening the spatial masks. Expanded validation_R43_shader_links records this failure and supersedes the earlier narrower PASS. No full review/cold proof or local-wear success credited. R44 corrects the socket and adds a recursive disabled-link gate.
