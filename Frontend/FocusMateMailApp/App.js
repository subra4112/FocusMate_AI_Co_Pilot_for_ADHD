import "react-native-gesture-handler";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer, DefaultTheme } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Feather } from "@expo/vector-icons";
import { HomeScreen } from "./src/screens/HomeScreen";
import { CalendarScreen } from "./src/screens/CalendarScreen";
import { VoiceScreen } from "./src/screens/VoiceScreen";
import { PlanScreen } from "./src/screens/PlanScreen";
import { colors } from "./src/theme";

const Tab = createBottomTabNavigator();

const navigationTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.accent,
    background: colors.background,
    card: colors.surface,
    text: colors.textPrimary,
    border: colors.divider,
    notification: colors.accent,
  },
};

export default function App() {
  return (
    <NavigationContainer theme={navigationTheme}>
      <StatusBar style="light" />
      <Tab.Navigator
        initialRouteName="Voice"
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarShowLabel: true,
          tabBarLabelStyle: {
            fontSize: 12,
            marginBottom: 6,
          },
          tabBarActiveTintColor: colors.accent,
          tabBarInactiveTintColor: colors.textMuted,
          tabBarStyle: {
            backgroundColor: colors.surface,
            borderTopColor: "rgba(15, 23, 42, 0.6)",
            height: 72,
            paddingBottom: 10,
            paddingTop: 10,
          },
          tabBarIcon: ({ color, size }) => {
            const iconName =
              route.name === "Voice"
                ? "mic"
                : route.name === "Calendar"
                ? "calendar"
                : route.name === "Inbox"
                ? "mail"
                : "sun";
            return <Feather name={iconName} size={size} color={color} />;
          },
        })}
      >
        <Tab.Screen
          name="Voice"
          component={VoiceScreen}
          options={{ title: "Voice" }}
        />
        <Tab.Screen
          name="Calendar"
          component={CalendarScreen}
          options={{ title: "Schedule" }}
        />
        <Tab.Screen
          name="Inbox"
          component={HomeScreen}
          options={{ title: "Messages" }}
        />
        <Tab.Screen
          name="Plan"
          component={PlanScreen}
          options={{ title: "Plan" }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
