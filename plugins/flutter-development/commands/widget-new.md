---
description: Create Flutter widget with Material 3 styling
model: claude-sonnet-4-5
---

Create a Flutter widget following Material 3 design patterns.

## Widget Specification

$ARGUMENTS

## Widget Patterns

### 1. **Stateless Widget**

```dart
import 'package:flutter/material.dart';

class ProjectCard extends StatelessWidget {
  final Project project;
  final VoidCallback? onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const ProjectCard({
    super.key,
    required this.project,
    this.onTap,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: colors.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.folder_outlined,
                  color: colors.onPrimaryContainer,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      project.name,
                      style: theme.textTheme.titleMedium,
                    ),
                    if (project.description != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        project.description!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colors.onSurfaceVariant,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              if (onEdit != null || onDelete != null)
                PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'edit') onEdit?.call();
                    if (value == 'delete') onDelete?.call();
                  },
                  itemBuilder: (context) => [
                    if (onEdit != null)
                      const PopupMenuItem(
                        value: 'edit',
                        child: ListTile(
                          leading: Icon(Icons.edit),
                          title: Text('Edit'),
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                    if (onDelete != null)
                      const PopupMenuItem(
                        value: 'delete',
                        child: ListTile(
                          leading: Icon(Icons.delete),
                          title: Text('Delete'),
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 2. **Consumer Widget (with Riverpod)**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class TimerWidget extends ConsumerWidget {
  const TimerWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timerState = ref.watch(timerProvider);
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              _formatDuration(timerState.elapsed),
              style: theme.textTheme.displayMedium?.copyWith(
                fontFeatures: [const FontFeature.tabularFigures()],
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (timerState.isRunning)
                  FilledButton.icon(
                    onPressed: () => ref.read(timerProvider.notifier).stop(),
                    icon: const Icon(Icons.stop),
                    label: const Text('Stop'),
                    style: FilledButton.styleFrom(
                      backgroundColor: colors.error,
                      foregroundColor: colors.onError,
                    ),
                  )
                else
                  FilledButton.icon(
                    onPressed: () => ref.read(timerProvider.notifier).start(1),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Start'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours.toString().padLeft(2, '0');
    final minutes = (duration.inMinutes % 60).toString().padLeft(2, '0');
    final seconds = (duration.inSeconds % 60).toString().padLeft(2, '0');
    return '$hours:$minutes:$seconds';
  }
}
```

### 3. **Form Widget**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class EntryForm extends ConsumerStatefulWidget {
  final TimeEntry? entry;
  final ValueChanged<TimeEntry> onSubmit;

  const EntryForm({
    super.key,
    this.entry,
    required this.onSubmit,
  });

  @override
  ConsumerState<EntryForm> createState() => _EntryFormState();
}

class _EntryFormState extends ConsumerState<EntryForm> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _descriptionController;
  String? _selectedProjectId;
  DateTime _startTime = DateTime.now();
  DateTime? _endTime;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _descriptionController = TextEditingController(
      text: widget.entry?.description,
    );
    if (widget.entry != null) {
      _selectedProjectId = widget.entry!.projectId;
      _startTime = widget.entry!.startTime;
      _endTime = widget.entry!.endTime;
    }
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final projectsAsync = ref.watch(projectsProvider());

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Project Dropdown
          projectsAsync.when(
            data: (projects) => DropdownButtonFormField<String>(
              value: _selectedProjectId,
              decoration: const InputDecoration(
                labelText: 'Project',
                prefixIcon: Icon(Icons.folder_outlined),
              ),
              items: projects.map((p) => DropdownMenuItem(
                value: p.id,
                child: Text(p.name),
              )).toList(),
              onChanged: (value) => setState(() => _selectedProjectId = value),
              validator: (value) =>
                  value == null ? 'Please select a project' : null,
            ),
            loading: () => const LinearProgressIndicator(),
            error: (_, __) => const Text('Failed to load projects'),
          ),

          const SizedBox(height: 16),

          // Description
          TextFormField(
            controller: _descriptionController,
            decoration: const InputDecoration(
              labelText: 'Description',
              prefixIcon: Icon(Icons.description_outlined),
            ),
            maxLines: 3,
          ),

          const SizedBox(height: 16),

          // Time Pickers
          Row(
            children: [
              Expanded(
                child: _DateTimePicker(
                  label: 'Start',
                  value: _startTime,
                  onChanged: (dt) => setState(() => _startTime = dt),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _DateTimePicker(
                  label: 'End',
                  value: _endTime,
                  onChanged: (dt) => setState(() => _endTime = dt),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Submit Button
          FilledButton(
            onPressed: _isSubmitting ? null : _submit,
            child: _isSubmitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(widget.entry == null ? 'Create' : 'Update'),
          ),
        ],
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final entry = TimeEntry(
        id: widget.entry?.id ?? '',
        projectId: _selectedProjectId!,
        startTime: _startTime,
        endTime: _endTime,
        description: _descriptionController.text.isEmpty
            ? null
            : _descriptionController.text,
      );
      widget.onSubmit(entry);
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
}
```

### 4. **Accessible Widget**

```dart
import 'package:flutter/material.dart';

class AccessibleCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData icon;
  final VoidCallback? onTap;
  final String? semanticLabel;

  const AccessibleCard({
    super.key,
    required this.title,
    this.subtitle,
    required this.icon,
    this.onTap,
    this.semanticLabel,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;

    return Semantics(
      label: semanticLabel ?? title,
      hint: onTap != null ? 'Double tap to open' : null,
      button: onTap != null,
      child: Card(
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                ExcludeSemantics(
                  child: Icon(
                    icon,
                    size: 32,
                    color: colors.primary,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: theme.textTheme.titleMedium,
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          subtitle!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colors.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                if (onTap != null)
                  ExcludeSemantics(
                    child: Icon(
                      Icons.chevron_right,
                      color: colors.onSurfaceVariant,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

Generate Flutter widgets with proper theming, accessibility, and Material 3 patterns.
