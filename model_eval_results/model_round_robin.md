# Model Round Robin

<style>
.matrix-table { border-collapse: collapse; margin: 12px 0 24px; }
.matrix-table th, .matrix-table td { border: 1px solid #999; padding: 8px 10px; text-align: center; vertical-align: middle; }
.matrix-table th { color: #000; }
.matrix-table thead th { background: #f3f3f3; color: #000; }
.matrix-row-header { background: #f9f9f9; font-weight: 600; color: #000; }
.matrix-corner { position: relative; min-width: 112px; width: 112px; height: 72px; padding: 0; background: linear-gradient(to bottom right, transparent 49.2%, #666 49.5%, #666 50.5%, transparent 50.8%), linear-gradient(135deg, #f9f9f9 0%, #f9f9f9 49.5%, #eef4ff 50.5%, #eef4ff 100%); }
.matrix-corner .corner-landlord { position: absolute; left: 10px; bottom: 8px; font-weight: 600; color: #000; }
.matrix-corner .corner-farmers { position: absolute; right: 10px; top: 8px; font-weight: 600; color: #000; }
.metric-cell { line-height: 1.4; white-space: nowrap; }
</style>

# Summary

| agent | avg_landlord_wp | avg_landlord_adp | avg_farmer_wp | avg_farmer_adp |
| --- | --- | --- | --- | --- |
| style_model | 0.5546 | 0.5672 | 0.6286 | 0.7399 |
| baseline_ADP | 0.6169 | 0.9404 | 0.7243 | 1.3992 |
| baseline_WP | 0.6515 | 0.8076 | 0.7616 | 1.2429 |
| baseline_SL | 0.5192 | 0.2885 | 0.6558 | 0.7193 |
| rlcard | 0.3283 | -1.0198 | 0.3519 | -1.0538 |
| random | 0.0737 | -2.2823 | 0.1337 | -2.3491 |

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
      <td><div class="metric-cell">wp_landlord=0.4641</div></td>
      <td><div class="metric-cell">wp_landlord=0.3202</div></td>
      <td><div class="metric-cell">wp_landlord=0.2863</div></td>
      <td><div class="metric-cell">wp_landlord=0.4267</div></td>
      <td><div class="metric-cell">wp_landlord=0.8466</div></td>
      <td><div class="metric-cell">wp_landlord=0.9836</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_ADP</th>
      <td><div class="metric-cell">wp_landlord=0.5523</div></td>
      <td><div class="metric-cell">wp_landlord=0.4233</div></td>
      <td><div class="metric-cell">wp_landlord=0.3702</div></td>
      <td><div class="metric-cell">wp_landlord=0.5151</div></td>
      <td><div class="metric-cell">wp_landlord=0.8593</div></td>
      <td><div class="metric-cell">wp_landlord=0.9810</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_WP</th>
      <td><div class="metric-cell">wp_landlord=0.5926</div></td>
      <td><div class="metric-cell">wp_landlord=0.4722</div></td>
      <td><div class="metric-cell">wp_landlord=0.4099</div></td>
      <td><div class="metric-cell">wp_landlord=0.5612</div></td>
      <td><div class="metric-cell">wp_landlord=0.8875</div></td>
      <td><div class="metric-cell">wp_landlord=0.9855</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_SL</th>
      <td><div class="metric-cell">wp_landlord=0.4133</div></td>
      <td><div class="metric-cell">wp_landlord=0.3013</div></td>
      <td><div class="metric-cell">wp_landlord=0.2501</div></td>
      <td><div class="metric-cell">wp_landlord=0.4076</div></td>
      <td><div class="metric-cell">wp_landlord=0.7842</div></td>
      <td><div class="metric-cell">wp_landlord=0.9587</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">rlcard</th>
      <td><div class="metric-cell">wp_landlord=0.1957</div></td>
      <td><div class="metric-cell">wp_landlord=0.1280</div></td>
      <td><div class="metric-cell">wp_landlord=0.1069</div></td>
      <td><div class="metric-cell">wp_landlord=0.1473</div></td>
      <td><div class="metric-cell">wp_landlord=0.4584</div></td>
      <td><div class="metric-cell">wp_landlord=0.9336</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">random</th>
      <td><div class="metric-cell">wp_landlord=0.0105</div></td>
      <td><div class="metric-cell">wp_landlord=0.0095</div></td>
      <td><div class="metric-cell">wp_landlord=0.0069</div></td>
      <td><div class="metric-cell">wp_landlord=0.0073</div></td>
      <td><div class="metric-cell">wp_landlord=0.0529</div></td>
      <td><div class="metric-cell">wp_landlord=0.3554</div></td>
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
      <td><div class="metric-cell">adp_landlord=-0.0624</div></td>
      <td><div class="metric-cell">adp_landlord=-1.0592</div></td>
      <td><div class="metric-cell">adp_landlord=-0.8442</div></td>
      <td><div class="metric-cell">adp_landlord=-0.2080</div></td>
      <td><div class="metric-cell">adp_landlord=2.3668</div></td>
      <td><div class="metric-cell">adp_landlord=3.2100</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_ADP</th>
      <td><div class="metric-cell">adp_landlord=0.4490</div></td>
      <td><div class="metric-cell">adp_landlord=-0.4354</div></td>
      <td><div class="metric-cell">adp_landlord=-0.3368</div></td>
      <td><div class="metric-cell">adp_landlord=0.3252</div></td>
      <td><div class="metric-cell">adp_landlord=2.4444</div></td>
      <td><div class="metric-cell">adp_landlord=3.1962</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_WP</th>
      <td><div class="metric-cell">adp_landlord=0.3670</div></td>
      <td><div class="metric-cell">adp_landlord=-0.5006</div></td>
      <td><div class="metric-cell">adp_landlord=-0.4538</div></td>
      <td><div class="metric-cell">adp_landlord=0.2766</div></td>
      <td><div class="metric-cell">adp_landlord=2.2512</div></td>
      <td><div class="metric-cell">adp_landlord=2.9050</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_SL</th>
      <td><div class="metric-cell">adp_landlord=-0.4582</div></td>
      <td><div class="metric-cell">adp_landlord=-1.1790</div></td>
      <td><div class="metric-cell">adp_landlord=-1.0932</div></td>
      <td><div class="metric-cell">adp_landlord=-0.3590</div></td>
      <td><div class="metric-cell">adp_landlord=1.8644</div></td>
      <td><div class="metric-cell">adp_landlord=2.9562</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">rlcard</th>
      <td><div class="metric-cell">adp_landlord=-1.9422</div></td>
      <td><div class="metric-cell">adp_landlord=-2.4250</div></td>
      <td><div class="metric-cell">adp_landlord=-2.2142</div></td>
      <td><div class="metric-cell">adp_landlord=-1.9466</div></td>
      <td><div class="metric-cell">adp_landlord=-0.2162</div></td>
      <td><div class="metric-cell">adp_landlord=2.6254</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">random</th>
      <td><div class="metric-cell">adp_landlord=-2.7928</div></td>
      <td><div class="metric-cell">adp_landlord=-2.7958</div></td>
      <td><div class="metric-cell">adp_landlord=-2.5152</div></td>
      <td><div class="metric-cell">adp_landlord=-2.4040</div></td>
      <td><div class="metric-cell">adp_landlord=-2.3880</div></td>
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
      <td><div class="metric-cell">wp_landlord=0.4641<br>adp_landlord=-0.0624</div></td>
      <td><div class="metric-cell">wp_landlord=0.3202<br>adp_landlord=-1.0592</div></td>
      <td><div class="metric-cell">wp_landlord=0.2863<br>adp_landlord=-0.8442</div></td>
      <td><div class="metric-cell">wp_landlord=0.4267<br>adp_landlord=-0.2080</div></td>
      <td><div class="metric-cell">wp_landlord=0.8466<br>adp_landlord=2.3668</div></td>
      <td><div class="metric-cell">wp_landlord=0.9836<br>adp_landlord=3.2100</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_ADP</th>
      <td><div class="metric-cell">wp_landlord=0.5523<br>adp_landlord=0.4490</div></td>
      <td><div class="metric-cell">wp_landlord=0.4233<br>adp_landlord=-0.4354</div></td>
      <td><div class="metric-cell">wp_landlord=0.3702<br>adp_landlord=-0.3368</div></td>
      <td><div class="metric-cell">wp_landlord=0.5151<br>adp_landlord=0.3252</div></td>
      <td><div class="metric-cell">wp_landlord=0.8593<br>adp_landlord=2.4444</div></td>
      <td><div class="metric-cell">wp_landlord=0.9810<br>adp_landlord=3.1962</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_WP</th>
      <td><div class="metric-cell">wp_landlord=0.5926<br>adp_landlord=0.3670</div></td>
      <td><div class="metric-cell">wp_landlord=0.4722<br>adp_landlord=-0.5006</div></td>
      <td><div class="metric-cell">wp_landlord=0.4099<br>adp_landlord=-0.4538</div></td>
      <td><div class="metric-cell">wp_landlord=0.5612<br>adp_landlord=0.2766</div></td>
      <td><div class="metric-cell">wp_landlord=0.8875<br>adp_landlord=2.2512</div></td>
      <td><div class="metric-cell">wp_landlord=0.9855<br>adp_landlord=2.9050</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">baseline_SL</th>
      <td><div class="metric-cell">wp_landlord=0.4133<br>adp_landlord=-0.4582</div></td>
      <td><div class="metric-cell">wp_landlord=0.3013<br>adp_landlord=-1.1790</div></td>
      <td><div class="metric-cell">wp_landlord=0.2501<br>adp_landlord=-1.0932</div></td>
      <td><div class="metric-cell">wp_landlord=0.4076<br>adp_landlord=-0.3590</div></td>
      <td><div class="metric-cell">wp_landlord=0.7842<br>adp_landlord=1.8644</div></td>
      <td><div class="metric-cell">wp_landlord=0.9587<br>adp_landlord=2.9562</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">rlcard</th>
      <td><div class="metric-cell">wp_landlord=0.1957<br>adp_landlord=-1.9422</div></td>
      <td><div class="metric-cell">wp_landlord=0.1280<br>adp_landlord=-2.4250</div></td>
      <td><div class="metric-cell">wp_landlord=0.1069<br>adp_landlord=-2.2142</div></td>
      <td><div class="metric-cell">wp_landlord=0.1473<br>adp_landlord=-1.9466</div></td>
      <td><div class="metric-cell">wp_landlord=0.4584<br>adp_landlord=-0.2162</div></td>
      <td><div class="metric-cell">wp_landlord=0.9336<br>adp_landlord=2.6254</div></td>
    </tr>
    <tr>
      <th class="matrix-row-header">random</th>
      <td><div class="metric-cell">wp_landlord=0.0105<br>adp_landlord=-2.7928</div></td>
      <td><div class="metric-cell">wp_landlord=0.0095<br>adp_landlord=-2.7958</div></td>
      <td><div class="metric-cell">wp_landlord=0.0069<br>adp_landlord=-2.5152</div></td>
      <td><div class="metric-cell">wp_landlord=0.0073<br>adp_landlord=-2.4040</div></td>
      <td><div class="metric-cell">wp_landlord=0.0529<br>adp_landlord=-2.3880</div></td>
      <td><div class="metric-cell">wp_landlord=0.3554<br>adp_landlord=-0.7982</div></td>
    </tr>
  </tbody>
</table>
