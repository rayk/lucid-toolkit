# Non-Obvious Patterns for Flutter Stack

Patterns Claude Opus 4.5 may not automatically apply. Include these in agent prompts.

> **Source Research:** [Riverpod docs](https://riverpod.dev/), [fpdart](https://pub.dev/packages/fpdart), [flutter_hooks](https://pub.dev/packages/flutter_hooks), [GoRouter](https://pub.dev/packages/go_router), [Code With Andrea](https://codewithandrea.com/)

---

## Riverpod 3.0

### Lifecycle & Disposal

| Pattern | Why Non-Obvious |
|---------|-----------------|
| Family providers MUST use `autoDispose` | Without it, each parameter combo creates permanent state → memory leak |
| Use `ref.keepAlive()` for conditional caching | Cache success, dispose failures: `result.isRight() ? ref.keepAlive() : null` |
| `ref.invalidate` doesn't show loading state | Use `AsyncValue.isRefreshing` in UI, not `isLoading` |
| Watching non-listened provider after `invalidate` delays recompute to next frame | Call `ref.refresh` if immediate recompute needed |

### ref.watch vs ref.read

| Rule | Why Non-Obvious |
|------|-----------------|
| NEVER use `ref.read` to "optimize" in build | Creates stale state bugs; `ref.watch` is designed for efficiency |
| Use `ref.select` for partial state | `ref.watch(provider.select((s) => s.count))` prevents unnecessary rebuilds |
| `ref.read` in notifier methods, `ref.watch` in `build()` | `ref.watch` in notifier creates circular dependency |
| After async gap in notifier, state may be stale | Always re-read or check `ref.mounted` after `await` |

### Code Generation (3.0)

| Pattern | Why Non-Obvious |
|---------|-----------------|
| All generated providers are `autoDispose` by default | Use `@Riverpod(keepAlive: true)` to persist |
| `Ref` unified in 3.0 (no more `AutoDisposeRef`) | Migration: remove type annotations specifying disposal |
| `riverpod_lint` catches `ref.watch` in callbacks | Enable lint rules - they catch 90% of common mistakes |

### AsyncNotifier Patterns

```dart
// NON-OBVIOUS: Check mounted after EVERY await
Future<void> updateItem(Item item) async {
  state = const AsyncLoading();
  final result = await ref.read(repoProvider).update(item).run();

  if (!ref.mounted) return;  // CRITICAL

  state = result.match(
    (f) => AsyncError(f, StackTrace.current),
    (r) => AsyncData(r),
  );
}

// NON-OBVIOUS: invalidateSelf for cache refresh
Future<void> refresh() async {
  ref.invalidateSelf();
  await future; // Wait for new data
}
```

---

## fpdart

### API Gotchas

| Pattern | Why Non-Obvious |
|---------|-----------------|
| `Option.match` parameter order: `None` first, `Some` second | Changed in v0.6.0, opposite of intuition |
| `fold` and `match` are identical on Either/Option | Use `match` for consistency, `fold` is alias |
| Foldable's `fold` was renamed to `foldLeft` | Breaking change, old code won't compile |
| Prefer Dart 3 `switch` over `match` for new code | Native pattern matching is more idiomatic |

### TaskEither Patterns

```dart
// NON-OBVIOUS: .run() is lazy - nothing executes until called
final task = TaskEither.tryCatch(...);
// Nothing happened yet!
final result = await task.run(); // NOW it executes

// NON-OBVIOUS: Use Do notation for sequential operations
TaskEither<Failure, Order> placeOrder(UserId id) {
  return TaskEither.Do(($) async {
    final user = await $(fetchUser(id));      // Short-circuits on Left
    final validated = $(validateUser(user));   // Sync Either works too
    return await $(createOrder(validated));
  });
}

// NON-OBVIOUS: Firebase never throws on network loss (offline mode)
// Can't rely on tryCatch for connectivity errors
TaskEither<Failure, Doc> fetchDoc(String id) {
  return TaskEither.tryCatch(
    () => firestore.doc(id).get(),
    (e, s) => NetworkFailure(e.toString()),
  ).flatMap((snap) => snap.exists
    ? TaskEither.right(Doc.fromSnap(snap))
    : TaskEither.left(NotFoundFailure()));
}
```

### Stream with Either

```dart
// NON-OBVIOUS: Firestore streams need onErrorReturnWith
Stream<Either<Failure, List<Item>>> watchItems() async* {
  yield* firestore.collection('items').snapshots()
    .map((snap) => Right<Failure, List<Item>>(
      snap.docs.map((d) => Item.fromJson(d.data())).toList()
    ))
    .onErrorReturnWith((e, s) => Left(FirestoreFailure(e.toString())));
}
```

---

## flutter_hooks

### Key Patterns

| Pattern | Why Non-Obvious |
|---------|-----------------|
| `useMemoized` + `useFuture` for async init | `useMemoized` caches the Future, `useFuture` unwraps it |
| `useEffect` keys trigger re-run, not dependencies | Different from React - explicitly list what should trigger |
| `useRef` for mutable state without rebuild | Returns `ObjectRef<T>`, mutate `.value` freely |
| `useCallback` is sugar for `useMemoized(() => () {...})` | Use for callbacks passed to child widgets |
| Hooks MUST be called unconditionally | No hooks inside `if` blocks or loops |
| Call order must be consistent across rebuilds | Hooks are stored by index, not name |

### Controller Pattern

```dart
// NON-OBVIOUS: Combine useMemoized + useEffect for controllers
Widget build(BuildContext context) {
  final tabController = useMemoized(
    () => TabController(length: 3, vsync: useSingleTickerProvider()),
    [/* keys that should recreate */],
  );

  useEffect(() {
    return tabController.dispose; // Cleanup on unmount
  }, [tabController]);

  return TabBarView(controller: tabController, ...);
}
```

### Async Pattern

```dart
// NON-OBVIOUS: Proper async initialization
Widget build(BuildContext context) {
  // Cache the Future (not the result)
  final prefsFuture = useMemoized(SharedPreferences.getInstance);
  // Unwrap with loading/error states
  final prefsSnapshot = useFuture(prefsFuture);

  return prefsSnapshot.when(
    data: (prefs) => SettingsView(prefs: prefs),
    loading: () => const CircularProgressIndicator(),
    error: (e, s) => ErrorView(error: e),
  );
}
```

---

## hooks_riverpod Integration

| Pattern | Why Non-Obvious |
|---------|-----------------|
| `HookConsumerWidget` combines hooks + Riverpod | Single widget type for both |
| Still need `flutter_hooks` dependency | `hooks_riverpod` doesn't include all hooks |
| Hooks for local state, Riverpod for global | Don't use hooks for what Riverpod does better |
| `useRef` for values that survive Riverpod rebuilds | Riverpod rebuilds don't reset hook state |

```dart
class MyWidget extends HookConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Riverpod for global state
    final user = ref.watch(userProvider);

    // Hooks for local UI state
    final controller = useTextEditingController();
    final isFocused = useState(false);

    return ...;
  }
}
```

---

## GoRouter + Riverpod Integration

### Authentication Redirect

```dart
// NON-OBVIOUS: AuthNotifier must implement Listenable for refreshListenable
// StateNotifier CANNOT be used (doesn't implement Listenable)

@riverpod
class Auth extends _$Auth with ChangeNotifier {
  @override
  AuthState build() {
    // Listen to auth changes
    ref.listen(firebaseAuthProvider, (_, next) {
      state = next.valueOrNull != null
        ? AuthState.authenticated(next.value!)
        : const AuthState.unauthenticated();
      notifyListeners(); // Trigger GoRouter refresh
    });
    return const AuthState.loading();
  }
}

@riverpod
GoRouter router(Ref ref) {
  final auth = ref.watch(authProvider.notifier);

  return GoRouter(
    refreshListenable: auth, // Auth must be Listenable
    redirect: (context, state) {
      final authState = ref.read(authProvider);

      // NON-OBVIOUS: Don't redirect during loading
      if (authState.isLoading) return null;

      final isAuth = authState.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');

      if (!isAuth && !isAuthRoute) {
        return '/auth/login?redirect=${state.matchedLocation}';
      }
      if (isAuth && isAuthRoute) {
        return state.uri.queryParameters['redirect'] ?? '/';
      }
      return null;
    },
    routes: [...],
  );
}
```

### StatefulShellRoute

```dart
// NON-OBVIOUS: GoRouter must NOT be created inline
// Creates "multiple widgets used same GlobalKey" on hot reload

// WRONG
MaterialApp.router(routerConfig: GoRouter(...))

// RIGHT - declare as provider or global
@riverpod
GoRouter router(Ref ref) => GoRouter(...);

// NON-OBVIOUS: parentNavigatorKey for routes outside shell
GoRoute(
  path: '/fullscreen',
  parentNavigatorKey: rootNavigatorKey, // Push over bottom nav
  builder: (context, state) => FullscreenPage(),
)

// NON-OBVIOUS: context.go() to tab resets its stack
// Use navigationShell.goBranch(index) to preserve state
StatefulShellRoute.indexedStack(
  builder: (context, state, navigationShell) {
    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (index) {
          navigationShell.goBranch(
            index,
            initialLocation: index == navigationShell.currentIndex,
          );
        },
        destinations: [...],
      ),
    );
  },
  branches: [...],
)
```

---

## Firebase + Riverpod

### StreamProvider Gotchas

| Pattern | Why Non-Obvious |
|---------|-----------------|
| Avoid nested StreamProviders (streams watching streams) | Use `.last` + `ref.watch` instead for composed streams |
| StreamProvider reloads show loading on every filter change | Use `AsyncValue.isRefreshing` or cache previous data |
| Firebase offline mode never throws on network loss | Can't detect connectivity via exceptions |
| Emulators must bind to `0.0.0.0`, not `localhost` | Android emulator can't reach `localhost` |
| Android emulator uses `10.0.2.2` for host machine | Not `localhost` or `127.0.0.1` |

### Auth + Firestore Composition

```dart
// NON-OBVIOUS: Return Stream.empty() not null for unauth
@riverpod
Stream<User?> currentUser(Ref ref) {
  final authState = ref.watch(authStateProvider);

  return authState.when(
    data: (user) {
      if (user == null) return Stream.value(null);
      return ref.watch(firestoreProvider)
        .doc('users/${user.uid}')
        .snapshots()
        .map((snap) => User.fromSnap(snap));
    },
    loading: () => Stream.empty(), // NOT Stream.value(null)
    error: (e, s) => Stream.error(e, s),
  );
}

// NON-OBVIOUS: Invalidate after mutation, don't update + invalidate
Future<void> updateProfile(User user) async {
  await ref.read(firestoreProvider)
    .doc('users/${user.id}')
    .update(user.toJson());

  // Just invalidate - don't set state then invalidate
  ref.invalidateSelf();
  await future; // Wait for fresh data
}
```

### Crashlytics Error Boundary

```dart
// NON-OBVIOUS: Two separate error handlers needed
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  // Flutter framework errors
  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterFatalError;

  // Async errors (Future/Stream)
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };

  runApp(const ProviderScope(child: MyApp()));
}
```

---

## Summary: Add to Agent Prompts

### Must Include (Non-Obvious)

1. `ref.mounted` check after every await in AsyncNotifier
2. Family providers need `autoDispose` to prevent memory leaks
3. `Option.match` has None first, Some second (unintuitive)
4. TaskEither is lazy - `.run()` executes it
5. Firebase never throws on network loss
6. GoRouter can't be created inline (GlobalKey issue)
7. `context.go()` to tab resets navigation stack
8. StreamProvider reloads on filter change (use isRefreshing)
9. Android emulator: `10.0.2.2` for host, emulators bind to `0.0.0.0`
10. `useEffect` keys vs React dependencies (different mental model)
11. Hooks must be called unconditionally and in same order
12. `HookConsumerWidget` for hooks + Riverpod together

### Can Omit (Claude Knows)

- Basic Either/Option/TaskEither syntax
- ref.watch in build, ref.read in callbacks
- Clean Architecture layer structure
- AsyncValue.when() pattern
- Basic GoRouter route definitions
- Standard Flutter hooks like useState, useEffect
- Riverpod @riverpod annotation syntax
