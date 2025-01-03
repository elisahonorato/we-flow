import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  StatusBar,
} from "react-native";
import { router } from "expo-router";
import { theme } from "@/src/theme";
import { IconSymbol } from "@/components/ui/IconSymbol";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { apiService } from "../services/apiService";

interface Event {
  id: number;
  title: string;
  description: string;
  date: string;
  category: string;
  status: "pending" | "completed" | "cancelled";
  priority: "high" | "medium" | "low";
}

const { width } = Dimensions.get("window");
const SPACING = 16;

export default function EventsScreen() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>("all");

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      // Aquí iría tu llamada a la API
      const response = await apiService.events.getAll();
      console.log(response, "elisa eventos");
      setEvents(response.data);
    } catch (error) {
      console.error("Error fetching events:", error);
      setError("Error al cargar los eventos");
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return theme.colors.error;
      case "medium":
        return theme.colors.warning;
      case "low":
        return theme.colors.success;
      default:
        return theme.colors.text;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return "checkmark.circle";
      case "cancelled":
        return "xmark.circle";
      default:
        return "clock";
    }
  };

  const filters = [
    { id: "all", label: "Todos" },
    { id: "pending", label: "Pendientes" },
    { id: "completed", label: "Completados" },
    { id: "cancelled", label: "Cancelados" },
  ];

  const filteredEvents = events.filter((event) =>
    selectedFilter === "all" ? true : event.status === selectedFilter
  );

  const renderEvent = ({ item }: { item: Event }) => {
    if (!item) return null;

    return (
      <TouchableOpacity style={styles.eventCard} activeOpacity={0.7}>
        <Text style={styles.eventTitle}>{item.title || "Sin título"}</Text>

        <Text style={styles.eventDescription} numberOfLines={2}>
          {item.description || "Sin descripción"}
        </Text>

        <View style={styles.eventFooter}>
          <View style={styles.dateContainer}>
            <IconSymbol name="calendar" size={16} color={theme.colors.text} />
            <Text style={styles.dateText}>
              {format(new Date(item.date), "d 'de' MMMM, yyyy", { locale: es })}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
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
        <TouchableOpacity style={styles.retryButton} onPress={fetchEvents}>
          <Text style={styles.retryText}>Reintentar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />

      <View style={styles.filtersContainer}>
        <FlatList
          horizontal
          data={filters}
          showsHorizontalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.filterButton,
                selectedFilter === item.id && styles.filterButtonActive,
              ]}
              onPress={() => setSelectedFilter(item.id)}
            >
              <Text
                style={[
                  styles.filterText,
                  selectedFilter === item.id && styles.filterTextActive,
                ]}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          )}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.filtersContent}
        />
      </View>

      <FlatList
        data={filteredEvents || []}
        renderItem={renderEvent}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <IconSymbol name="calendar" size={64} color={theme.colors.text} />
            <Text style={styles.emptyText}>No hay eventos disponibles</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: SPACING,
    backgroundColor: theme.colors.primary,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: theme.colors.text,
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: theme.colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  filtersContainer: {
    marginTop: SPACING,
  },
  filtersContent: {
    paddingHorizontal: SPACING,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterText: {
    color: theme.colors.text,
    fontWeight: "500",
  },
  filterTextActive: {
    color: theme.colors.text,
    fontWeight: "600",
  },
  listContainer: {
    padding: SPACING,
    paddingBottom: SPACING * 4,
  },
  eventCard: {
    backgroundColor: theme.colors.background,
    borderRadius: 16,
    padding: SPACING,
    marginBottom: SPACING,
    elevation: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  eventHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  priorityBadge: {
    flexDirection: "row",
    alignItems: "center",
  },
  priorityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  priorityText: {
    fontSize: 12,
    color: theme.colors.text,
    opacity: 0.7,
  },
  eventTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: theme.colors.text,
    marginBottom: 8,
  },
  eventDescription: {
    fontSize: 14,
    color: theme.colors.text,
    opacity: 0.8,
    marginBottom: 12,
  },
  eventFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  dateContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  dateText: {
    fontSize: 12,
    color: theme.colors.text,
    marginLeft: 4,
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: theme.colors.primary,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 12,
    color: theme.colors.text,
    fontWeight: "500",
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
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: SPACING * 4,
  },
  emptyText: {
    fontSize: 16,
    color: theme.colors.text,
    opacity: 0.7,
    marginTop: SPACING,
  },
});
