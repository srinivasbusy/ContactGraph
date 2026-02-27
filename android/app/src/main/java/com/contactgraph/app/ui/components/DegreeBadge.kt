package com.contactgraph.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.contactgraph.app.R
import com.contactgraph.app.ui.theme.Degree1Color
import com.contactgraph.app.ui.theme.Degree2Color
import com.contactgraph.app.ui.theme.Degree3Color
import com.contactgraph.app.ui.theme.Degree4PlusColor

@Composable
fun DegreeBadge(
    degree: Int,
    modifier: Modifier = Modifier
) {
    val (label, color) = when (degree) {
        1 -> stringResource(R.string.degree_1st) to Degree1Color
        2 -> stringResource(R.string.degree_2nd) to Degree2Color
        3 -> stringResource(R.string.degree_3rd) to Degree3Color
        else -> stringResource(R.string.degree_n_plus, degree) to Degree4PlusColor
    }

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .background(
                color = color.copy(alpha = 0.15f),
                shape = RoundedCornerShape(12.dp)
            )
            .padding(horizontal = 8.dp, vertical = 3.dp)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.SemiBold,
            color = color
        )
    }
}
