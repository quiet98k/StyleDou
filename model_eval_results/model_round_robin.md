# Model Round Robin

<style>
.matrix-table { border-collapse: collapse; margin: 12px 0 24px; }
.matrix-table th, .matrix-table td { border: 1px solid #999; padding: 8px 10px; text-align: center; vertical-align: middle; }
.matrix-table thead th { background: #f3f3f3; }
.matrix-row-header { background: #f9f9f9; font-weight: 600; }
.matrix-corner { position: relative; min-width: 112px; width: 112px; height: 72px; padding: 0; background: linear-gradient(to bottom right, transparent 49.2%, #666 49.5%, #666 50.5%, transparent 50.8%), linear-gradient(135deg, #f9f9f9 0%, #f9f9f9 49.5%, #eef4ff 50.5%, #eef4ff 100%); }
.matrix-corner .corner-landlord { position: absolute; left: 10px; bottom: 8px; font-weight: 600; color: #000; }
.matrix-corner .corner-farmers { position: absolute; right: 10px; top: 8px; font-weight: 600; color: #000; }
.metric-cell { line-height: 1.4; white-space: nowrap; }
</style>

# Summary

| agent | avg_landlord_wp | avg_landlord_adp | avg_farmer_wp | avg_farmer_adp |
| --- | --- | --- | --- | --- |
| style_model | 0.5516 | 0.5822 | 0.6284 | 0.7379 |
| baseline_ADP | 0.6165 | 0.9654 | 0.7255 | 1.4036 |
| baseline_WP | 0.6516 | 0.8281 | 0.7633 | 1.2549 |
| baseline_SL | 0.5183 | 0.2992 | 0.6545 | 0.7208 |
| rlcard | 0.3284 | -1.0205 | 0.3549 | -1.0663 |
| random | 0.0733 | -2.3128 | 0.1338 | -2.3924 |

# Landlord Win Rate Matrix

<table class="matrix-table">
  <thead>
    <tr>
      <th class="matrix-corner"><span class="corner-farmers">Farmers</span><span class="corner-landlord">Landlord</span></th>
      <th>style_model</th>
      <th>baseline_ADP</th>
      <th>baseline_WP</th>
      <th>baseline_SL</th>
      <th>rlcard</th>
      <th>random</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th class="matrix-row-header">style_model</th>
      <td><div class="metric-cell">wp_landlord=0.4611</div></td>
      <td><div class="metric-cell">wp_landlord=0.3129</div></td>
      <td><div class="metric-cell">wp_landlord=0.2759</div></td>
      <td><div class="metric-cell">wp_landlord=0.4282</div></td>
      <td><div class="metric-cell">wp_landlord=0.8480</div></td>
      <td><div class="metric-cell">wp_landlord=0.9836</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_ADP</th>
      <td><div class="metric-cell">wp_landlord=0.5524</div></td>
      <td><div class="metric-cell">wp_landlord=0.4248</div></td>
      <td><div class="metric-cell">wp_landlord=0.3688</div></td>
      <td><div class="metric-cell">wp_landlord=0.5182</div></td>
      <td><div class="metric-cell">wp_landlord=0.8528</div></td>
      <td><div class="metric-cell">wp_landlord=0.9822</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_WP</th>
      <td><div class="metric-cell">wp_landlord=0.5925</div></td>
      <td><div class="metric-cell">wp_landlord=0.4703</div></td>
      <td><div class="metric-cell">wp_landlord=0.4146</div></td>
      <td><div class="metric-cell">wp_landlord=0.5659</div></td>
      <td><div class="metric-cell">wp_landlord=0.8812</div></td>
      <td><div class="metric-cell">wp_landlord=0.9849</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_SL</th>
      <td><div class="metric-cell">wp_landlord=0.4187</div></td>
      <td><div class="metric-cell">wp_landlord=0.3003</div></td>
      <td><div class="metric-cell">wp_landlord=0.2505</div></td>
      <td><div class="metric-cell">wp_landlord=0.4035</div></td>
      <td><div class="metric-cell">wp_landlord=0.7799</div></td>
      <td><div class="metric-cell">wp_landlord=0.9567</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">rlcard</th>
      <td><div class="metric-cell">wp_landlord=0.1951</div></td>
      <td><div class="metric-cell">wp_landlord=0.1303</div></td>
      <td><div class="metric-cell">wp_landlord=0.1027</div></td>
      <td><div class="metric-cell">wp_landlord=0.1498</div></td>
      <td><div class="metric-cell">wp_landlord=0.4609</div></td>
      <td><div class="metric-cell">wp_landlord=0.9317</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">random</th>
      <td><div class="metric-cell">wp_landlord=0.0098</div></td>
      <td><div class="metric-cell">wp_landlord=0.0085</div></td>
      <td><div class="metric-cell">wp_landlord=0.0079</div></td>
      <td><div class="metric-cell">wp_landlord=0.0073</div></td>
      <td><div class="metric-cell">wp_landlord=0.0480</div></td>
      <td><div class="metric-cell">wp_landlord=0.3584</div></td>
    </tr>
  </tbody>
</table>

# Landlord ADP Matrix

<table class="matrix-table">
  <thead>
    <tr>
      <th class="matrix-corner"><span class="corner-farmers">Farmers</span><span class="corner-landlord">Landlord</span></th>
      <th>style_model</th>
      <th>baseline_ADP</th>
      <th>baseline_WP</th>
      <th>baseline_SL</th>
      <th>rlcard</th>
      <th>random</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th class="matrix-row-header">style_model</th>
      <td><div class="metric-cell">adp_landlord=-0.0754</div></td>
      <td><div class="metric-cell">adp_landlord=-1.0714</div></td>
      <td><div class="metric-cell">adp_landlord=-0.8876</div></td>
      <td><div class="metric-cell">adp_landlord=-0.1944</div></td>
      <td><div class="metric-cell">adp_landlord=2.4388</div></td>
      <td><div class="metric-cell">adp_landlord=3.2832</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_ADP</th>
      <td><div class="metric-cell">adp_landlord=0.4486</div></td>
      <td><div class="metric-cell">adp_landlord=-0.4060</div></td>
      <td><div class="metric-cell">adp_landlord=-0.3124</div></td>
      <td><div class="metric-cell">adp_landlord=0.3478</div></td>
      <td><div class="metric-cell">adp_landlord=2.4586</div></td>
      <td><div class="metric-cell">adp_landlord=3.2556</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_WP</th>
      <td><div class="metric-cell">adp_landlord=0.3674</div></td>
      <td><div class="metric-cell">adp_landlord=-0.4932</div></td>
      <td><div class="metric-cell">adp_landlord=-0.4180</div></td>
      <td><div class="metric-cell">adp_landlord=0.3096</div></td>
      <td><div class="metric-cell">adp_landlord=2.2730</div></td>
      <td><div class="metric-cell">adp_landlord=2.9300</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_SL</th>
      <td><div class="metric-cell">adp_landlord=-0.4000</div></td>
      <td><div class="metric-cell">adp_landlord=-1.1856</div></td>
      <td><div class="metric-cell">adp_landlord=-1.1082</div></td>
      <td><div class="metric-cell">adp_landlord=-0.3894</div></td>
      <td><div class="metric-cell">adp_landlord=1.8870</div></td>
      <td><div class="metric-cell">adp_landlord=2.9914</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">rlcard</th>
      <td><div class="metric-cell">adp_landlord=-1.9586</div></td>
      <td><div class="metric-cell">adp_landlord=-2.4392</div></td>
      <td><div class="metric-cell">adp_landlord=-2.2582</div></td>
      <td><div class="metric-cell">adp_landlord=-1.9592</div></td>
      <td><div class="metric-cell">adp_landlord=-0.2004</div></td>
      <td><div class="metric-cell">adp_landlord=2.6924</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">random</th>
      <td><div class="metric-cell">adp_landlord=-2.8096</div></td>
      <td><div class="metric-cell">adp_landlord=-2.8260</div></td>
      <td><div class="metric-cell">adp_landlord=-2.5448</div></td>
      <td><div class="metric-cell">adp_landlord=-2.4390</div></td>
      <td><div class="metric-cell">adp_landlord=-2.4590</div></td>
      <td><div class="metric-cell">adp_landlord=-0.7982</div></td>
    </tr>
  </tbody>
</table>

# Combined Landlord Metrics Matrix

<table class="matrix-table">
  <thead>
    <tr>
      <th class="matrix-corner"><span class="corner-farmers">Farmers</span><span class="corner-landlord">Landlord</span></th>
      <th>style_model</th>
      <th>baseline_ADP</th>
      <th>baseline_WP</th>
      <th>baseline_SL</th>
      <th>rlcard</th>
      <th>random</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th class="matrix-row-header">style_model</th>
      <td><div class="metric-cell">wp_landlord=0.4611<br>adp_landlord=-0.0754</div></td>
      <td><div class="metric-cell">wp_landlord=0.3129<br>adp_landlord=-1.0714</div></td>
      <td><div class="metric-cell">wp_landlord=0.2759<br>adp_landlord=-0.8876</div></td>
      <td><div class="metric-cell">wp_landlord=0.4282<br>adp_landlord=-0.1944</div></td>
      <td><div class="metric-cell">wp_landlord=0.8480<br>adp_landlord=2.4388</div></td>
      <td><div class="metric-cell">wp_landlord=0.9836<br>adp_landlord=3.2832</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_ADP</th>
      <td><div class="metric-cell">wp_landlord=0.5524<br>adp_landlord=0.4486</div></td>
      <td><div class="metric-cell">wp_landlord=0.4248<br>adp_landlord=-0.4060</div></td>
      <td><div class="metric-cell">wp_landlord=0.3688<br>adp_landlord=-0.3124</div></td>
      <td><div class="metric-cell">wp_landlord=0.5182<br>adp_landlord=0.3478</div></td>
      <td><div class="metric-cell">wp_landlord=0.8528<br>adp_landlord=2.4586</div></td>
      <td><div class="metric-cell">wp_landlord=0.9822<br>adp_landlord=3.2556</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_WP</th>
      <td><div class="metric-cell">wp_landlord=0.5925<br>adp_landlord=0.3674</div></td>
      <td><div class="metric-cell">wp_landlord=0.4703<br>adp_landlord=-0.4932</div></td>
      <td><div class="metric-cell">wp_landlord=0.4146<br>adp_landlord=-0.4180</div></td>
      <td><div class="metric-cell">wp_landlord=0.5659<br>adp_landlord=0.3096</div></td>
      <td><div class="metric-cell">wp_landlord=0.8812<br>adp_landlord=2.2730</div></td>
      <td><div class="metric-cell">wp_landlord=0.9849<br>adp_landlord=2.9300</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_SL</th>
      <td><div class="metric-cell">wp_landlord=0.4187<br>adp_landlord=-0.4000</div></td>
      <td><div class="metric-cell">wp_landlord=0.3003<br>adp_landlord=-1.1856</div></td>
      <td><div class="metric-cell">wp_landlord=0.2505<br>adp_landlord=-1.1082</div></td>
      <td><div class="metric-cell">wp_landlord=0.4035<br>adp_landlord=-0.3894</div></td>
      <td><div class="metric-cell">wp_landlord=0.7799<br>adp_landlord=1.8870</div></td>
      <td><div class="metric-cell">wp_landlord=0.9567<br>adp_landlord=2.9914</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">rlcard</th>
      <td><div class="metric-cell">wp_landlord=0.1951<br>adp_landlord=-1.9586</div></td>
      <td><div class="metric-cell">wp_landlord=0.1303<br>adp_landlord=-2.4392</div></td>
      <td><div class="metric-cell">wp_landlord=0.1027<br>adp_landlord=-2.2582</div></td>
      <td><div class="metric-cell">wp_landlord=0.1498<br>adp_landlord=-1.9592</div></td>
      <td><div class="metric-cell">wp_landlord=0.4609<br>adp_landlord=-0.2004</div></td>
      <td><div class="metric-cell">wp_landlord=0.9317<br>adp_landlord=2.6924</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">random</th>
      <td><div class="metric-cell">wp_landlord=0.0098<br>adp_landlord=-2.8096</div></td>
      <td><div class="metric-cell">wp_landlord=0.0085<br>adp_landlord=-2.8260</div></td>
      <td><div class="metric-cell">wp_landlord=0.0079<br>adp_landlord=-2.5448</div></td>
      <td><div class="metric-cell">wp_landlord=0.0073<br>adp_landlord=-2.4390</div></td>
      <td><div class="metric-cell">wp_landlord=0.0480<br>adp_landlord=-2.4590</div></td>
      <td><div class="metric-cell">wp_landlord=0.3584<br>adp_landlord=-0.7982</div></td>
    </tr>
  </tbody>
</table>
