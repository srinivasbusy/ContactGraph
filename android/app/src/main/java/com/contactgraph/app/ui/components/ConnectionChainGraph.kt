package com.contactgraph.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.TextMeasurer
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.sp
import com.contactgraph.app.data.model.ConnectionChain
import com.contactgraph.app.ui.theme.Degree1Color
import com.contactgraph.app.ui.theme.Degree2Color
import com.contactgraph.app.ui.theme.Degree3Color
import com.contactgraph.app.ui.theme.Degree4PlusColor
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun ConnectionChainGraph(
    chain: ConnectionChain,
    modifier: Modifier = Modifier
) {
    val textMeasurer = rememberTextMeasurer()
    val surfaceColor = MaterialTheme.colorScheme.surfaceVariant
    val onSurfaceColor = MaterialTheme.colorScheme.onSurface

    // Pre-compute node positions as equidistant points along the chain
    val nodes = buildList {
        add(Pair("You", 0))
        chain.path.forEachIndexed { index, node ->
            add(Pair(node.name, index + 1))
        }
    }

    Canvas(modifier = modifier.background(surfaceColor)) {
        val nodeCount = nodes.size
        if (nodeCount == 0) return@Canvas

        val nodeRadius = 28f
        val horizontalStep = if (nodeCount > 1) size.width / (nodeCount + 1) else size.width / 2f
        val centerY = size.height / 2f

        val positions = nodes.mapIndexed { index, _ ->
            Offset(
                x = horizontalStep * (index + 1),
                y = centerY
            )
        }

        // Draw edges first
        for (i in 0 until positions.size - 1) {
            val color = degreeColor(i + 1)
            drawLine(
                color = color.copy(alpha = 0.7f),
                start = positions[i],
                end = positions[i + 1],
                strokeWidth = 4f
            )
        }

        // Draw nodes on top
        nodes.forEachIndexed { index, (name, _) ->
            val pos = positions[index]
            val degree = index
            val nodeColor = degreeColor(degree)

            // Shadow
            drawCircle(
                color = Color.Black.copy(alpha = 0.15f),
                radius = nodeRadius + 3f,
                center = pos.copy(y = pos.y + 3f)
            )
            // Node fill
            drawCircle(color = nodeColor, radius = nodeRadius, center = pos)
            // Node border
            drawCircle(
                color = Color.White.copy(alpha = 0.5f),
                radius = nodeRadius,
                center = pos,
                style = androidx.compose.ui.graphics.drawscope.Stroke(width = 2f)
            )

            // Label below node
            val label = truncateLabel(name)
            drawIntoCanvas { canvas ->
                val paint = android.graphics.Paint().apply {
                    color = onSurfaceColor.toArgb()
                    textSize = 26f
                    textAlign = android.graphics.Paint.Align.CENTER
                    isAntiAlias = true
                }
                canvas.nativeCanvas.drawText(
                    label,
                    pos.x,
                    pos.y + nodeRadius + 36f,
                    paint
                )
            }
        }
    }
}

private const val NODE_LABEL_MAX_LENGTH = 8

private fun truncateLabel(name: String): String =
    if (name.length > NODE_LABEL_MAX_LENGTH) name.take(NODE_LABEL_MAX_LENGTH - 1) + "…" else name
    0 -> Color(0xFF6650A4) // "You" - primary purple
    1 -> Degree1Color
    2 -> Degree2Color
    3 -> Degree3Color
    else -> Degree4PlusColor
}
