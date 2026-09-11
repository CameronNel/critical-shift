# R10 saved-artifact cold-open verification

**PASS for artifact survival and independently reviewed visual stability. Not bit-identical.**

The exact comparison remains [REVIEW](R10-cold-start.md), with every numerical difference recorded. Across ten images, at most 0.05095% of RGB channels changed; maximum difference 9/255, maximum mean absolute difference 0.0006269/255. No comparison tolerance was increased or failed result overwritten.

Fresh-file geometry/dependency/camera checks plus all ten successful renders and independent Luna inspection of cold images. User requires saved-artifact survival; bit-exact GPU pixels are reported separately and are not claimed.

Independent assessment: [Luna cold review](../critics/luna-R10-cold-review.md). Saved Blender SHA256: `cdc0b48a5af6cb11bae6a4511074cc4b9aacf4dce687503e55d3891a49bb2693`. Geometry, assigned materials, native text, cameras and connection metadata survive reopening. Live MCP's built-in-font sentinel warning is retained in the live inspection report.

Not bit-identical. Differences over one 8-bit channel step localize to conformed HX shell lettering; numerical surface sensitivity is an inference, not a proven renderer diagnosis. Historical exact-pixel REVIEW is retained unchanged. No runtime or whole-map claim.
