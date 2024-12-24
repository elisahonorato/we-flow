import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  Image,
  StatusBar,
  ScrollView,
} from "react-native";
import { useCategories } from "../contexts/categories";
import { theme } from "@/src/theme";
import { Category } from "../types/category";
import { router } from "expo-router";
import { IconSymbol } from "@/components/ui/IconSymbol";

const { width } = Dimensions.get("window");
const SPACING = 16;
const CARD_WIDTH = (width - SPACING * 3) / 2;

export default function ActionScreen() {
  const { categories, selectedCategory, setSelectedCategory, loading, error } =
    useCategories();
  const [isCategoriesExpanded, setIsCategoriesExpanded] = useState(false);

  const handleCategoryPress = (category: Category) => {
    setSelectedCategory(category);
    router.push("/(tabs)/category-detail");
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => window.location.reload()}
        >
          <Text style={styles.retryText}>Reintentar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const renderIcon = (base64Icon: string) => {
    try {
      if (!base64Icon) return null;
      const imageUri = base64Icon.startsWith("data:")
        ? base64Icon
        : `data:image/png;base64,${base64Icon}`;
      return (
        <Image
          source={{ uri: imageUri }}
          style={styles.iconImage}
          resizeMode="contain"
        />
      );
    } catch (error) {
      return null;
    }
  };

  const renderCategoryCard = (item: Category) => {
    const isSelected = selectedCategory?.id === item.id;

    return (
      <TouchableOpacity
        key={item.id}
        style={[
          styles.categoryCard,
          isSelected && { borderColor: theme.colors.primary },
        ]}
        onPress={() => handleCategoryPress(item)}
      >
        <View style={styles.iconContainer}>
          {item.icon ? (
            renderIcon(item.icon)
          ) : (
            <IconSymbol
              name="category"
              size={24}
              color={theme.colors.primary}
            />
          )}
        </View>
        <Text style={styles.categoryCardTitle}>{item.name}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>WE-FLOW</Text>
      </View>

      {/* Wrap everything in a ScrollView */}
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Main Actions */}
        <View style={styles.mainActions}>
          <TouchableOpacity
            style={[
              styles.actionCard,
              { backgroundColor: theme.colors.primary },
            ]}
            onPress={() => router.push("/(tabs)/events")}
          >
            <IconSymbol name="calendar" size={32} color={theme.colors.text} />
            <Text style={styles.actionTitle}>Eventos</Text>
            <Text style={styles.actionSubtitle}>Ver próximos eventos</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.actionCard,
              { backgroundColor: theme.colors.accent },
            ]}
            onPress={() => setIsCategoriesExpanded(!isCategoriesExpanded)}
          >
            <IconSymbol name="category" size={32} color={theme.colors.text} />
            <Text style={styles.actionTitle}>Categorías</Text>
            <Text style={styles.actionSubtitle}>
              Explorar o Elegir categorías
            </Text>
          </TouchableOpacity>
        </View>

        {/* Expanded Categories Section */}
        {isCategoriesExpanded && (
          <View style={styles.expandedCategories}>
            <Text style={styles.sectionTitle}>Todas las Categorías</Text>
            <View style={styles.categoriesGrid}>
              {categories.map(renderCategoryCard)}
            </View>
          </View>
        )}
      </ScrollView>

      {/* Siempre mostrar el banner, pero con diferente contenido */}
      <View style={styles.selectedBanner}>
        {selectedCategory ? (
          <>
            <View style={styles.selectedIconContainer}>
              {selectedCategory.icon ? (
                renderIcon(selectedCategory.icon)
              ) : (
                <IconSymbol
                  name="category"
                  size={24}
                  color={theme.colors.primary}
                />
              )}
            </View>
            <Text style={styles.selectedBannerText}>
              Categoría seleccionada: {selectedCategory.name}
            </Text>
            <TouchableOpacity
              style={styles.clearButton}
              onPress={() => setSelectedCategory(null)}
            >
              <IconSymbol name="close" size={20} color={theme.colors.text} />
            </TouchableOpacity>
          </>
        ) : (
          <Text style={styles.selectedBannerText}>
            No hay categoría seleccionada
          </Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: SPACING,
    paddingTop: SPACING * 3,
    backgroundColor: theme.colors.primary,
    alignItems: "center",
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: theme.colors.text,
  },
  mainActions: {
    flexDirection: "column",
    padding: SPACING,
    gap: SPACING,
  },
  actionCard: {
    padding: SPACING * 1.5,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    elevation: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
  },
  actionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: theme.colors.text,
    marginTop: SPACING,
  },
  actionSubtitle: {
    fontSize: 14,
    color: theme.colors.text,
    opacity: 0.8,
    marginTop: 4,
    textAlign: "center",
  },
  recentSection: {
    padding: SPACING,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: SPACING,
  },
  recentList: {
    paddingRight: SPACING,
  },
  recentCard: {
    width: 120,
    marginRight: SPACING,
    padding: SPACING,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    alignItems: "center",
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: theme.colors.background,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 8,
  },
  iconImage: {
    width: "70%",
    height: "70%",
  },
  recentCardTitle: {
    fontSize: 14,
    fontWeight: "500",
    color: theme.colors.text,
    textAlign: "center",
  },
  selectedBanner: {
    flexDirection: "row",
    alignItems: "center",
    margin: SPACING,
    padding: SPACING,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    elevation: 3,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  selectedIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.background,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  selectedBannerText: {
    flex: 1,
    fontSize: 16,
    fontWeight: "600",
    color: theme.colors.text,
  },
  clearButton: {
    padding: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: SPACING * 2,
  },
  errorText: {
    fontSize: 16,
    color: theme.colors.error,
    textAlign: "center",
    marginBottom: 16,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
  },
  retryText: {
    color: theme.colors.text,
    fontWeight: "600",
  },
  expandedCategories: {
    padding: SPACING,
  },
  categoriesGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: SPACING,
  },
  categoryCard: {
    width: CARD_WIDTH,
    padding: SPACING,
    backgroundColor: theme.colors.card,
    borderRadius: 12,
    alignItems: "center",
    elevation: 2,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    borderWidth: 2,
    borderColor: "transparent",
  },
  categoryCardTitle: {
    fontSize: 14,
    fontWeight: "500",
    color: theme.colors.text,
    textAlign: "center",
    marginTop: 8,
  },
  scrollContent: {
    flexGrow: 1,
  },
});
