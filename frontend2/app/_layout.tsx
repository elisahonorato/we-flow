import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider,
} from "@react-navigation/native";
import { useFonts } from "expo-font";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import "react-native-reanimated";
import { ScrollLayout } from "@/components/ScrollLayout";
import { useColorScheme } from "@/hooks/useColorScheme";
import { Redirect } from "expo-router";
import { AuthProvider } from "./contexts/auth";
import { theme } from "@/src/theme";
import { CategoriesProvider } from "./contexts/categories";
import { GestureHandlerRootView } from "react-native-gesture-handler";

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <ThemeProvider value={theme}>
          <CategoriesProvider>
            <ScrollLayout>
              <Stack
                screenOptions={{
                  headerStyle: {
                    backgroundColor: theme.colors.background,
                  },
                  headerTintColor: theme.colors.text,
                  headerTitleStyle: {
                    fontSize: theme.typography.sizes.title,
                    fontFamily: theme.typography.fonts.primary.regular,
                  },
                }}
              >
                <Stack.Screen
                  name="(auth)/sign-in"
                  options={{ headerShown: false }}
                />
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="+not-found" />
              </Stack>
              <StatusBar style="auto" />
            </ScrollLayout>
          </CategoriesProvider>
        </ThemeProvider>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}
