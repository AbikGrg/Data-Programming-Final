# main.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from extensions import db
from models import DataSet, DataEntry
import csv, io
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

# --- Public Routes ---
@main.route('/')
def index():
    return render_template('index.html')

# Show the dashboard with all datasets belonging to the logged-in user

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to view the dashboard.")
        return redirect(url_for('auth.login'))
    user_id = session.get('user_id')
    datasets = DataSet.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', datasets=datasets)

# Allow logged-in users to upload a CSV file (handles both GET and POST requests)

@main.route('/upload', methods=['GET', 'POST'])
def upload_data():
    if 'user_id' not in session:
        flash("Please log in to upload files.")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file:
            flash("No file selected.")
            return redirect(url_for('main.upload_data'))
        filename = secure_filename(file.filename)
        # Open file with proper newline handling
        text_stream = io.TextIOWrapper(file.stream, encoding='utf-8', newline='')
        reader = csv.reader(text_stream)
        headers = next(reader, None)
        if headers is None:
            flash("CSV file is empty or invalid.")
            return redirect(url_for('main.upload_data'))
        headers = headers[:10]  # Limit to 10 columns
        dataset = DataSet(user_id=session['user_id'], name=filename, headers=','.join(headers))
        db.session.add(dataset)
        db.session.flush()  # Get dataset.id before commit
        for row in reader:
            row = row[:10]
            if len(row) < len(headers):
                row += [''] * (len(headers) - len(row))
            entry = DataEntry(dataset_id=dataset.id)
            for i, value in enumerate(row, start=1):
                setattr(entry, f'col{i}', value)
            db.session.add(entry)
        db.session.commit()
        flash("File uploaded successfully.")
        return redirect(url_for('main.view_dataset', dataset_id=dataset.id))
    return render_template('upload.html')

# Route to view a specific dataset (only if the user is logged in and owns the dataset)

@main.route('/dashboard/<int:dataset_id>')
def view_dataset(dataset_id):
    if 'user_id' not in session:
        flash("Please log in to view dataset.")
        return redirect(url_for('auth.login'))
    dataset = DataSet.query.get_or_404(dataset_id)
    if dataset.user_id != session.get('user_id'):
        flash("You do not have permission to view this dataset.")
        return redirect(url_for('main.dashboard'))
    headers = dataset.headers.split(',')
    entries = DataEntry.query.filter_by(dataset_id=dataset.id).all()
    data = [[getattr(entry, f'col{i}') for i in range(1, len(headers)+1)] for entry in entries]
    return render_template('view_dataset.html', dataset=dataset, headers=headers, data=data)

# --- API Endpoints for Data Access & Interaction ---
@main.route('/api/data/<int:dataset_id>', methods=['GET'])
def get_data(dataset_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    dataset = DataSet.query.get_or_404(dataset_id)
    if dataset.user_id != session.get('user_id') and session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    query = DataEntry.query.filter_by(dataset_id=dataset_id)
    # Apply dynamic filtering (e.g., ?col1=value)
    for i in range(1, 11):
        col_param = request.args.get(f'col{i}')
        if col_param:
            query = query.filter(getattr(DataEntry, f'col{i}').ilike(f"%{col_param}%"))
    # Pagination support
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    headers = dataset.headers.split(',')
    data_list = []
    for entry in pagination.items:
        row = { headers[idx]: getattr(entry, f'col{idx+1}') for idx in range(len(headers)) }
        row['id'] = entry.id  # Include entry ID for actions
        data_list.append(row)
    return jsonify({
        'dataset': dataset.name,
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'data': data_list
    })

# API route to update a data entry (only allowed for the owner or an admin)

@main.route('/api/data/entry/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    entry = DataEntry.query.get_or_404(entry_id)
    dataset = entry.dataset
    if dataset.user_id != session.get('user_id') and session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    update_data = request.get_json()
    if not update_data:
        return jsonify({'error': 'No update data provided'}), 400
    headers = dataset.headers.split(',')
    for idx, header in enumerate(headers):
        if header in update_data:
            setattr(entry, f'col{idx+1}', update_data[header])
    db.session.commit()
    return jsonify({'message': 'Entry updated successfully.'})

# API route to delete a data entry (only allowed for the owner or an admin)

@main.route('/api/data/entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    entry = DataEntry.query.get_or_404(entry_id)
    dataset = entry.dataset
    if dataset.user_id != session.get('user_id') and session.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted successfully.'})

# Route to delete a dataset (only if the user is logged in)

@main.route('/dataset/delete/<int:dataset_id>', methods=['POST'])
def delete_dataset(dataset_id):
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('auth.login'))

    dataset = DataSet.query.get_or_404(dataset_id)

    # Ensuring user owns the dataset or is an admin
    if dataset.user_id != session.get('user_id') and session.get('role') != 'admin':
        flash("You do not have permission to delete this dataset.")
        return redirect(url_for('main.dashboard'))

    # Deletes the dataset and everything linked to it (if it's set up that way).
    db.session.delete(dataset)
    db.session.commit()

    flash("Dataset deleted successfully.")
    return redirect(url_for('main.dashboard'))
