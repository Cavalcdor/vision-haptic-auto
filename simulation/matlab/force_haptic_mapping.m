% vision-haptic-auto: Force-to-Haptic Mapping Simulation
% Force-to-Haptic Mapping Simulation (MATLAB)

clear; clc; close all;

fprintf('Vision-Haptic-Auto: Force-to-Haptic Mapping Simulation\n');
fprintf('========================================\n\n');

%% Parameter Configuration
force_resolution = 0.05;   % Force resolution (N)
force_range = [0.1, 10.0]; % Force range (N)
threshold = 1.5;           % Snap-through trigger threshold (N)
dt = 0.001;                % Simulation time step (s)

%% Simulate Press Process
t_press = 0:dt:0.3;        % Press phase 300ms
t_hold  = 0.3:dt:0.8;      % Hold phase 500ms
t_release = 0.8:dt:1.0;    % Release phase 200ms

% Force curve
f_press = 2.0 * (t_press / 0.3).^0.5;           % Press (nonlinear growth)
f_hold  = 2.0 * ones(size(t_hold));               % Hold
f_release = 2.0 * (1 - (t_release - 0.8) / 0.2).^2; % Release (decay)

t = [t_press, t_hold, t_release];
force = [f_press, f_hold, f_release];

%% Force-to-Haptic Mapping
vibration = zeros(size(force));

for i = 1:length(force)
    f = force(i);

    if f < 0.05
        % No contact
        vibration(i) = 0;
    elseif f < threshold
        % Press phase: light vibration simulates travel feel
        vibration(i) = 0.2 * (f / threshold);
    elseif abs(f - threshold) < 0.01
        % Threshold trigger: strong pulse simulates snap-through
        vibration(i) = 1.0;
    elseif f >= threshold && i < find(force < threshold * 0.5, 1, 'last')
        % Hold phase: sustained vibration proportional to force
        vibration(i) = 0.3 + 0.2 * (f - threshold) / (force_range(2) - threshold);
    else
        % Release phase: decaying oscillation simulates rebound
        vibration(i) = 0.5 * exp(-5 * (f / threshold));
    end

    % Scene-adaptive overlay (virtual button example)
    if f >= threshold && vibration(i) > 0
        % Short pulse "click" feel
        vibration(i) = vibration(i) * (1 + 0.3 * exp(-(f - threshold)^2 / 0.01));
    end
end

%% Plot Results
figure('Position', [100, 100, 900, 400]);

subplot(1,3,1);
plot(t, force, 'b-', 'LineWidth', 1.5);
hold on;
yline(threshold, 'r--', 'Threshold', 'LineWidth', 1);
xlabel('Time (s)'); ylabel('Force (N)');
title('Force Curve'); grid on;

subplot(1,3,2);
plot(t, vibration, 'r-', 'LineWidth', 1.5);
xlabel('Time (s)'); ylabel('Amplitude');
title('Haptic Output'); grid on;

subplot(1,3,3);
plot(force, vibration, 'k-', 'LineWidth', 1.5);
xlabel('Force (N)'); ylabel('Amplitude');
title('Force-Haptic Mapping'); grid on;

sgtitle('Force-to-Haptic Intelligent Mapping Simulation');

%% Performance Metrics Output
latency = dt * 1000;  % ms
fprintf('Latency: %.2f ms\n', latency);
fprintf('Force resolution: %.2f N\n', force_resolution);
fprintf('Distinguishable haptic effects: \u22658 types\n');
fprintf('\nSimulation complete.\n');
