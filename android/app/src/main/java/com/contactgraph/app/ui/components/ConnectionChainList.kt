package com.contactgraph.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.contactgraph.app.R
import com.contactgraph.app.data.model.ConnectionChain
import com.contactgraph.app.ui.theme.Degree1Color
import com.contactgraph.app.ui.theme.Degree2Color
import com.contactgraph.app.ui.theme.Degree3Color
import com.contactgraph.app.ui.theme.Degree4PlusColor

@Composable
fun ConnectionChainList(
    chain: ConnectionChain,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = stringResource(R.string.connection_breadcrumb_header),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(12.dp))

            // Build the full breadcrumb list: You → node1 (1st) → node2 (2nd) → target (Nth)
            val allNodes = buildList {
                add(Pair("You", 0))
                chain.path.forEachIndexed { index, node ->
                    add(Pair(node.name, index + 1))
                }
            }

            allNodes.forEachIndexed { index, (name, degree) ->
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    if (index > 0) {
                        Icon(
                            imageVector = Icons.Filled.ArrowForward,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    Text(
                        text = name,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = if (index == 0 || index == allNodes.lastIndex) FontWeight.Bold else FontWeight.Normal
                    )
                    if (degree > 0) {
                        Spacer(modifier = Modifier.width(6.dp))
                        DegreeBadge(degree = degree)
                    }
                }

                if (index < allNodes.lastIndex) {
                    Spacer(modifier = Modifier.height(6.dp))
                }
            }
        }
    }
}
