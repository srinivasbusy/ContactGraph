package com.contactgraph.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.navArgument
import com.contactgraph.app.ui.screens.auth.LoginScreen
import com.contactgraph.app.ui.screens.home.HomeScreen
import com.contactgraph.app.ui.screens.home.SearchResultScreen
import com.contactgraph.app.ui.screens.network.NetworkScreen
import com.contactgraph.app.ui.screens.profile.ProfileScreen

sealed class Screen(val route: String, val label: String) {
    object Login : Screen("login", "Login")
    object Home : Screen("home", "Home")
    object SearchResult : Screen("search_result/{query}", "Search Result") {
        fun createRoute(query: String) = "search_result/$query"
    }
    object Network : Screen("network", "Network")
    object Profile : Screen("profile", "Profile")
}

private val bottomNavItems = listOf(
    Triple(Screen.Home, Icons.Filled.Home, "Home"),
    Triple(Screen.Network, Icons.Filled.Share, "Network"),
    Triple(Screen.Profile, Icons.Filled.Person, "Profile")
)

@Composable
fun NavGraph(
    navController: NavHostController,
    contactsPermissionGranted: Boolean,
    startDestination: String = Screen.Login.route
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val showBottomBar = currentDestination?.route in listOf(
        Screen.Home.route,
        Screen.Network.route,
        Screen.Profile.route,
        Screen.SearchResult.route
    )

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    bottomNavItems.forEach { (screen, icon, label) ->
                        NavigationBarItem(
                            icon = { Icon(icon, contentDescription = label) },
                            label = { Text(label) },
                            selected = currentDestination?.hierarchy?.any {
                                it.route == screen.route
                            } == true,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = startDestination,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Login.route) {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate(Screen.Home.route) {
                            popUpTo(Screen.Login.route) { inclusive = true }
                        }
                    }
                )
            }

            composable(Screen.Home.route) {
                HomeScreen(
                    onSearch = { query ->
                        navController.navigate(Screen.SearchResult.createRoute(query))
                    }
                )
            }

            composable(
                route = Screen.SearchResult.route,
                arguments = listOf(navArgument("query") { type = NavType.StringType })
            ) { backStackEntry ->
                val query = backStackEntry.arguments?.getString("query") ?: ""
                SearchResultScreen(
                    query = query,
                    onBack = { navController.navigateUp() }
                )
            }

            composable(Screen.Network.route) {
                NetworkScreen()
            }

            composable(Screen.Profile.route) {
                ProfileScreen(
                    onSignOut = {
                        navController.navigate(Screen.Login.route) {
                            popUpTo(0) { inclusive = true }
                        }
                    }
                )
            }
        }
    }
}
