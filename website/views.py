from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Event, HomePageContent, Team, Match

views = Blueprint('views', __name__)

@views.route('/')
def home():
    # Filter events where the end_date is greater than the current date and time
    active_events = Event.query.filter(Event.end_date > datetime.now()).all()
    home_content = HomePageContent.query.first()
    # If no homepage content exists, create a default one.
    if not home_content:
        from . import db
        home_content = HomePageContent()
        db.session.add(home_content)
        db.session.commit()
    return render_template('home.html', events=active_events, home_content=home_content)


@views.route('/event/<int:event_id>/match-fixtures')
@login_required
def match_fixtures(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if the event belongs to the current user
    if event.admin_id != current_user.id:
        flash('You do not have permission to view these matches.', 'error')
        return redirect(url_for('add_event.event_page', event_id=event_id))

    teams = event.teams
    matches = event.matches
    return render_template('match_fixtures.html', event=event, teams=teams, matches=matches)

@views.route('/update-score/<int:match_id>', methods=['POST'])
@login_required
def update_score(match_id):
    match = Match.query.get_or_404(match_id)
    event_id = match.event_id

    # Check if the match belongs to the current user
    if match.admin_id != current_user.id:
        if request.is_json:
            return jsonify({'success': False, 'error': 'You do not have permission to update this match score.'})
        flash('You do not have permission to update this match score.', 'error')
        return redirect(url_for('add_event.event_page', event_id=event_id))

    if request.is_json:
        data = request.get_json()
        team = data.get('team')
        score = data.get('score')
    else:
        team = request.form.get('team')
        score = request.form.get('score')

    try:
        if team == 'a':
            match.team_a_score = int(score)
        elif team == 'b':
            match.team_b_score = int(score)
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid team specified.'})
            flash('Invalid team specified.', 'error')
            return redirect(url_for('add_event.event_page', event_id=event_id))

        db.session.commit()
        if request.is_json:
            return jsonify({'success': True})
        flash('Score updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': 'Error updating score.'})
        flash('Error updating score. Please try again.', 'error')

    return redirect(url_for('add_event.event_page', event_id=event_id))

@views.route('/create-match', methods=['POST'])
@login_required
def create_match():
    team_a_id = request.form.get('team_a_id')
    team_b_id = request.form.get('team_b_id')
    date_time = request.form.get('date_time')
    event_id = request.form.get('event_id')
    team_a_score = request.form.get('team_a_score')
    team_b_score = request.form.get('team_b_score')

    if team_a_id == team_b_id:
        flash('Team A and Team B cannot be the same team!', 'error')
        return redirect(url_for('add_event.event_page', event_id=event_id))

    try:
        match = Match(
            team_a_id=team_a_id,
            team_b_id=team_b_id,
            date_time=datetime.strptime(date_time, '%Y-%m-%dT%H:%M'),
            event_id=event_id,
            admin_id=current_user.id
        )

        # Add scores if provided
        if team_a_score:
            match.team_a_score = int(team_a_score)
        if team_b_score:
            match.team_b_score = int(team_b_score)

        db.session.add(match)
        db.session.commit()
        flash('Match created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating match. Please try again.', 'error')

    return redirect(url_for('add_event.event_page', event_id=event_id))

@views.route('/edit-match/<int:match_id>', methods=['GET', 'POST'])
@login_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    event_id = match.event_id

    # Check if the match belongs to the current user
    if match.admin_id != current_user.id:
        flash('You do not have permission to edit this match.', 'error')
        return redirect(url_for('add_event.event_page', event_id=event_id))

    if request.method == 'GET':
        return render_template('edit_match.html', match=match, event=match.event, teams=match.event.teams)

    team_a_id = request.form.get('team_a_id')
    team_b_id = request.form.get('team_b_id')
    date_time = request.form.get('date_time')
    team_a_score = request.form.get('team_a_score')
    team_b_score = request.form.get('team_b_score')

    if team_a_id == team_b_id:
        flash('Team A and Team B cannot be the same team!', 'error')
        return redirect(url_for('add_event.event_page', event_id=event_id))

    try:
        match.team_a_id = team_a_id
        match.team_b_id = team_b_id
        match.date_time = datetime.strptime(date_time, '%Y-%m-%dT%H:%M')

        # Update scores if provided
        if team_a_score:
            match.team_a_score = int(team_a_score)
        if team_b_score:
            match.team_b_score = int(team_b_score)

        db.session.commit()
        flash('Match updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating match. Please try again.', 'error')

    return redirect(url_for('add_event.event_page', event_id=event_id))

@views.route('/delete-match/<int:match_id>', methods=['POST'])
@login_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    event_id = match.event_id

    # Check if the match belongs to the current user
    if match.admin_id != current_user.id:
        flash('You do not have permission to delete this match.', 'error')
        return redirect(url_for('add_event.event_page', event_id=event_id))

    try:
        db.session.delete(match)
        db.session.commit()
        flash('Match deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting match. Please try again.', 'error')

    return redirect(url_for('add_event.event_page', event_id=event_id))
