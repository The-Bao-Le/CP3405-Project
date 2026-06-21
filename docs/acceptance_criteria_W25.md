## Acceptance Criteria — W25

1. **Prediction coverage**

   * The W25 prediction file includes forecasts for:

     * SPX
     * NDX
     * IWM
     * Technology
     * Energy
     * Financials
     * Utilities
     * Materials
   * Each market target includes a clear directional prediction, such as **up**, **down**, or **neutral**.
   * Each prediction includes short supporting reasoning from at least one automated agent output.

2. **Almanac agent automation**

   * The Almanac agent runs automatically through the GitHub Actions workflow.
   * The agent produces a structured output file, preferably JSON or CSV.
   * The output includes calendar-based market context such as earnings season, FOMC timing, options expiry, seasonal patterns, major economic events, or relevant market calendar risks.
   * The output file is saved in the repository using a clear W25 filename, for example:

     * `data/w25/almanac_snapshot_W25.json`
     * `data/w25/almanac_snapshot_W25.csv`

3. **Technical agent automation**

   * The Technical agent runs automatically through the GitHub Actions workflow.
   * The agent produces a structured output file, preferably JSON or CSV.
   * The output covers SPX, NDX, IWM, Technology, Energy, Financials, Utilities, and Materials.
   * The output includes relevant technical indicators such as recent return, moving average trend, RSI, volatility, or price momentum.
   * The output file is saved in the repository using a clear W25 filename, for example:

     * `data/w25/technical_snapshot_W25.json`
     * `data/w25/technical_snapshot_W25.csv`

4. **GitHub Actions workflow**

   * The automation workflow can run without manual data collection.
   * The workflow successfully installs dependencies, runs both agents, and commits or saves the generated output files.
   * The repository includes evidence of a successful workflow run.
   * The workflow can also be triggered manually for testing using `workflow_dispatch`.

5. **Calibration log automation**

   * The calibration script compares W25 predictions against actual W25 market outcomes.
   * The calibration score uses the same scoring method from W22 to keep results comparable across weeks.
   * The calibration process generates both a human-readable log and a structured result file, for example:

     * `calibration/calibration_log_W25.md`
     * `calibration/calibration_result_W25.json`
   * The calibration log clearly shows each prediction item, actual result, hit/miss outcome, and score contribution.

6. **Delta Engine output**

   * The Delta Engine calculates the difference between predicted and actual market direction or movement.
   * The output identifies where the forecast was correct, incorrect, or partially aligned.
   * The Delta Engine result is saved as a file and can be referenced in the presentation or retrospective.

7. **Documentation**

   * The repository includes short documentation explaining:

     * what each automated agent does,
     * what files are generated,
     * how to run the workflow,
     * how the calibration score is calculated.
   * The documentation is clear enough for another team member to reproduce the process.

8. **Presentation readiness**

   * The team can show that at least two agents produced structured output files automatically.
   * The team can explain how the automated outputs supported the W25 prediction.
   * The team can explain that the calibration scoring rule was reused from W22 for consistency.
